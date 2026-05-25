"""AK Lumora Backend — FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import asyncio
import shutil
import time
from typing import Dict, Optional, Set

from app.config import settings
from app.database import create_tables, async_session
from app.routers import auth, drive, folders, uploads, face_search
from app.services.file_monitor import file_monitor
from app.websocket import manager
from app.models.folder import WatchedFolder
from app.models.upload import UploadLog
from sqlalchemy import select

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main_loop = None

# ── Backend public URL (used for preview URLs etc.) ──────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "https://aklumora-production.up.railway.app")

async def _safe_notify_new_file(folder_id: int, file_path: str):
    try:
        await _notify_new_file(folder_id, file_path)
    except Exception as e:
        logger.exception(f"Unhandled error processing {file_path}: {e}")

async def _notify_deleted_file(folder_id: int, file_path: str):
    """Handle when a file is deleted from the local disk."""
    async with async_session() as db:
        result = await db.execute(
            select(UploadLog).where(UploadLog.folder_id == folder_id, UploadLog.file_path == file_path)
        )
        log = result.scalar_one_or_none()
        if log:
            user_id = log.user_id
            await db.delete(log)
            await db.commit()
            
            message = {
                "type": "delete_file",
                "file_path": file_path,
                "folder_id": folder_id
            }
            await manager.send_to_user(user_id, message)
            logger.info(f"Cleaned up deleted file from DB: {file_path}")

def on_new_file(folder_id: int, file_path: str):
    """Callback from file monitor when a new image is detected."""
    logger.info(f"New file callback: folder={folder_id}, path={file_path}")
    if main_loop and not main_loop.is_closed():
        asyncio.run_coroutine_threadsafe(_safe_notify_new_file(folder_id, file_path), main_loop)
    else:
        logger.error("Main loop is not available to process new file")

def on_deleted_file(folder_id: int, file_path: str):
    """Callback from file monitor when an image is deleted."""
    if main_loop and not main_loop.is_closed():
        asyncio.run_coroutine_threadsafe(_notify_deleted_file(folder_id, file_path), main_loop)


def _make_safe_filename(folder_id: int, file_name: str) -> str:
    safe_name = file_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    return f"folder_{folder_id}_{int(time.time())}_{safe_name}"


async def _notify_new_file(folder_id: int, file_path: str):
    """Send WebSocket notification about a new file and upload it to Drive."""
    file_name = os.path.basename(file_path)
    
    # Wait until the file is fully accessible to avoid WinError 32 (file lock)
    for _ in range(10):
        try:
            with open(file_path, "rb"):
                pass
            break
        except OSError:
            await asyncio.sleep(0.5)
            
    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    _, ext = os.path.splitext(file_name)

    async with async_session() as db:
        result = await db.execute(select(WatchedFolder).where(WatchedFolder.id == folder_id))
        folder = result.scalar_one_or_none()
        if not folder:
            logger.warning(f"No watched folder found for id {folder_id}")
            return

        log = UploadLog(
            user_id=folder.user_id,
            folder_id=folder_id,
            file_name=file_name,
            file_path=file_path,
            file_format=ext.lower(),
            file_size_mb=round(file_size / 1024 / 1024, 2) if file_size else None,
            preview_url=None,  # Will be set below
            drive_file_id=None,
            public_link=None,
            status='pending',
            error_message=None,
            upload_time_sec=None,
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        
        # ✅ FIX: Use BACKEND_URL instead of hardcoded localhost
        preview_url = f"{BACKEND_URL}/api/uploads/stream/{log.id}"
        log.preview_url = preview_url
        await db.commit()

        message = {
            "type": "new_file",
            "upload_log_id": log.id,
            "folder_id": folder_id,
            "folder_name": folder.folder_name,
            "file_name": file_name,
            "file_path": file_path,
            "preview_url": preview_url,
            "file_size": file_size,
            "file_format": ext.lower(),
            "drive_file_id": None,
            "public_link": None,
            "upload_status": "pending",
            "error_message": None,
            "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        }

        await manager.send_to_user(folder.user_id, message)

        # ── Enqueue for background face-embedding generation ──────
        from app.services import face_queue as fq_mod
        from app.services.face_queue import FaceTask

        queue = fq_mod.face_queue
        if queue is not None:
            await queue.enqueue(
                FaceTask(
                    upload_log_id=log.id,
                    user_id=folder.user_id,
                    folder_id=folder_id,
                    file_path=file_path,
                    drive_file_id=None,  # set later after Drive upload
                )
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    global main_loop
    main_loop = asyncio.get_running_loop()
    
    logger.info("🚀 AK Lumora Backend starting...")
    await create_tables()
    file_monitor.set_callback(on_new_file, on_deleted_file)

    # Create uploads directory and managed-folders root
    os.makedirs("uploads", exist_ok=True)
    from app.routers.folders import MANAGED_FOLDERS_ROOT
    os.makedirs(MANAGED_FOLDERS_ROOT, exist_ok=True)

    # Auto-start watchers for already configured folders
    async with async_session() as db:
        result = await db.execute(select(WatchedFolder).where(WatchedFolder.is_watching == True))
        watched_folders = result.scalars().all()
        for folder in watched_folders:
            normalized_path = os.path.normpath(folder.local_path)
            # If the stored path doesn't exist (cloud deployment), use a managed dir
            if not os.path.isdir(normalized_path):
                managed_path = os.path.join(MANAGED_FOLDERS_ROOT, str(folder.id))
                os.makedirs(managed_path, exist_ok=True)
                normalized_path = managed_path
                logger.info(f"Cloud mode: remapped folder {folder.id} → {managed_path} (in-memory)")
            started = file_monitor.start_watching(folder.id, normalized_path)
            if started:
                logger.info(f"Resumed watching folder {folder.id}: {normalized_path}")
            else:
                logger.warning(f"Failed to resume watcher for folder {folder.id}: {normalized_path}")

    logger.info("✅ Database tables created")

    # ── Initialize face detection services ──────────────────────
    from app.services.face_service import face_service
    from app.services.vector_store import VectorStore
    from app.services.face_queue import FaceQueueManager
    import app.services.vector_store as vs_mod
    import app.services.face_queue as fq_mod

    try:
        face_service.initialize(settings.FACE_MODEL_PREFERENCE)
        logger.info("✅ Face detection model loaded: %s", face_service.model_name)
    except Exception as exc:
        logger.warning("⚠️ Face detection unavailable: %s", exc)

    try:
        vs_mod.vector_store = VectorStore(settings.QDRANT_STORAGE_PATH)
        logger.info("✅ Vector store ready at %s", settings.QDRANT_STORAGE_PATH)
    except Exception as exc:
        logger.warning("⚠️ Vector store unavailable: %s", exc)

    try:
        fq_mod.face_queue = FaceQueueManager(
            max_workers=settings.FACE_MAX_WORKERS
        )
        fq_mod.face_queue.start()
        logger.info("✅ Face queue started (%d workers)", fq_mod.face_queue.max_workers)
    except Exception as exc:
        logger.warning("⚠️ Face queue unavailable: %s", exc)

    yield

    logger.info("🛑 Shutting down...")
    file_monitor.stop_all()

    # Drain face queue gracefully
    if fq_mod.face_queue is not None:
        try:
            await fq_mod.face_queue.stop()
            logger.info("✅ Face queue drained")
        except Exception:
            pass

    # Close qdrant client explicitly before interpreter teardown to avoid
    # noisy __del__ ImportError during Python shutdown.
    if vs_mod.vector_store is not None:
        try:
            vs_mod.vector_store.close()
            logger.info("✅ Vector store closed")
        except Exception as exc:
            logger.warning("⚠️ Vector store close warning: %s", exc)
        finally:
            vs_mod.vector_store = None


app = FastAPI(
    title="AK Lumora API",
    description="Backend API for AK Lumora — Photography Studio Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://ak-lumora.vercel.app",
        "https://ak-lumora-6uqej2nar-abhishekcodepoint3690-7089s-projects.vercel.app",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(drive.router)
app.include_router(folders.router)
app.include_router(uploads.router)
app.include_router(face_search.router)


@app.get("/")
async def root():
    return {"message": "AK Lumora API", "status": "running", "version": "1.0.0"}


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.websocket("/ws/live/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket for real-time file monitoring updates."""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages (ping/pong, etc.)
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
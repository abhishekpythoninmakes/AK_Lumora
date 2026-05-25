"""Face search API router.

Endpoints for uploading a selfie (file or base64), running face detection,
searching the Qdrant vector store, and returning matching images.
The frontend fetches the actual images from Drive — the backend only
returns metadata + Drive file IDs.
"""

import base64
import logging
import time
from typing import Optional, List

import psutil
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.face import FaceEmbedding, PersonCluster
from app.models.folder import WatchedFolder
from app.models.upload import UploadLog
from app.schemas.face import (
    FaceEmbeddingResponse,
    FaceQueueStatus,
    FaceSearchBase64Request,
    FaceSearchResponse,
    FaceSearchResult,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/face-search", tags=["Face Search"])


# ── Helpers ───────────────────────────────────────────────────────────

async def _build_results(
    hits: list,
    db: AsyncSession,
) -> List[FaceSearchResult]:
    """Enrich Qdrant hits with upload-log / folder metadata."""
    if not hits:
        return []

    # Collect upload_log_ids for batch lookup
    log_ids = list(
        {h["payload"].get("upload_log_id") for h in hits if h["payload"].get("upload_log_id")}
    )
    if not log_ids:
        return []

    # Fetch upload logs + folder names in one query
    rows = (
        await db.execute(
            select(UploadLog, WatchedFolder)
            .join(WatchedFolder, UploadLog.folder_id == WatchedFolder.id)
            .where(UploadLog.id.in_(log_ids))
        )
    ).all()

    log_map = {}
    for log, folder in rows:
        log_map[log.id] = (log, folder)

    results: List[FaceSearchResult] = []
    seen_uploads = set()  # deduplicate same image appearing for multiple faces

    for hit in hits:
        uid = hit["payload"].get("upload_log_id")
        if uid in seen_uploads:
            continue
        seen_uploads.add(uid)

        log_folder = log_map.get(uid)
        if not log_folder:
            continue
        log, folder = log_folder

        drive_file_id = log.drive_file_id or hit["payload"].get("drive_file_id") or ""
        
        public_link = log.public_link
        if not public_link and drive_file_id:
            public_link = f"https://drive.google.com/uc?export=view&id={drive_file_id}"
            
        thumbnail_url = log.thumbnail_url
        if not thumbnail_url and drive_file_id:
            thumbnail_url = f"https://drive.google.com/thumbnail?id={drive_file_id}&sz=w800"

        results.append(
            FaceSearchResult(
                face_embedding_id=hit["id"],
                upload_log_id=uid,
                drive_file_id=drive_file_id,
                similarity=round(hit["score"], 4),
                confidence=hit["payload"].get("confidence", 0.0),
                person_id=hit["payload"].get("person_id"),
                folder_id=folder.id,
                folder_name=folder.folder_name,
                drive_folder_name=folder.drive_folder_name,
                file_name=log.file_name,
                file_size=log.file_size_mb,
                public_link=public_link,
                thumbnail_url=thumbnail_url,
                created_at=log.created_at,
            )
        )

    return results


# ── Search by file upload ─────────────────────────────────────────────

@router.post("/search", response_model=FaceSearchResponse)
async def search_by_face(
    user_id: int,
    file: UploadFile = File(...),
    threshold: float = Query(0.45, ge=0.1, le=1.0),
    limit: int = Query(50, ge=1, le=200),
    folder_ids: Optional[str] = Query(None, description="Comma-separated folder IDs"),
    db: AsyncSession = Depends(get_db),
):
    """Upload a selfie image → detect face → search for matches."""
    from app.services.face_service import face_service
    from app.services import vector_store as vs_mod

    if not face_service.ready:
        raise HTTPException(503, "Face detection model not loaded yet")

    store = vs_mod.vector_store
    if store is None:
        raise HTTPException(503, "Vector store not initialized")

    t0 = time.perf_counter()

    # Read image bytes
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty image file")

    # Detect faces
    import asyncio

    faces = await asyncio.to_thread(face_service.process_image_bytes, data)
    if not faces:
        return FaceSearchResponse(
            face_detected=False,
            threshold_used=threshold,
            search_time_ms=round((time.perf_counter() - t0) * 1000, 1),
        )

    # Use the first (largest / most confident) face
    query_face = max(faces, key=lambda f: f.confidence)

    # Parse folder_ids
    fids = None
    if folder_ids:
        try:
            fids = [int(x.strip()) for x in folder_ids.split(",") if x.strip()]
        except ValueError:
            pass

    # Search Qdrant
    hits = await asyncio.to_thread(
        store.search,
        query_face.embedding,
        user_id,
        limit,
        threshold,
        fids,
    )

    # Enrich results
    results = await _build_results(hits, db)

    elapsed = round((time.perf_counter() - t0) * 1000, 1)
    return FaceSearchResponse(
        face_detected=True,
        face_count=len(faces),
        matches=results,
        total_matches=len(results),
        threshold_used=threshold,
        search_time_ms=elapsed,
    )


# ── Search by base64 (camera capture) ────────────────────────────────

@router.post("/search-base64", response_model=FaceSearchResponse)
async def search_by_base64(
    body: FaceSearchBase64Request,
    db: AsyncSession = Depends(get_db),
):
    """Search using a base64-encoded image (from camera capture)."""
    from app.services.face_service import face_service
    from app.services import vector_store as vs_mod

    if not face_service.ready:
        raise HTTPException(503, "Face detection model not loaded yet")

    store = vs_mod.vector_store
    if store is None:
        raise HTTPException(503, "Vector store not initialized")

    t0 = time.perf_counter()

    # Decode base64
    try:
        # Handle data-URL prefix ("data:image/jpeg;base64,...")
        raw = body.image_base64
        if "," in raw:
            raw = raw.split(",", 1)[1]
        data = base64.b64decode(raw)
    except Exception:
        raise HTTPException(400, "Invalid base64 image data")

    import asyncio

    faces = await asyncio.to_thread(face_service.process_image_bytes, data)
    if not faces:
        return FaceSearchResponse(
            face_detected=False,
            threshold_used=body.threshold,
            search_time_ms=round((time.perf_counter() - t0) * 1000, 1),
        )

    query_face = max(faces, key=lambda f: f.confidence)

    hits = await asyncio.to_thread(
        store.search,
        query_face.embedding,
        body.user_id,
        body.limit,
        body.threshold,
        body.folder_ids,
    )

    results = await _build_results(hits, db)

    elapsed = round((time.perf_counter() - t0) * 1000, 1)
    return FaceSearchResponse(
        face_detected=True,
        face_count=len(faces),
        matches=results,
        total_matches=len(results),
        threshold_used=body.threshold,
        search_time_ms=elapsed,
    )


# ── Queue status ──────────────────────────────────────────────────────

@router.get("/queue-status", response_model=FaceQueueStatus)
async def get_queue_status(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get face processing queue and system status."""
    from app.services import face_queue as fq_mod
    from app.services import vector_store as vs_mod

    queue = fq_mod.face_queue
    store = vs_mod.vector_store

    total_faces = 0
    total_persons = 0

    if store:
        import asyncio

        total_faces = await asyncio.to_thread(store.count, user_id)

    persons_result = await db.execute(
        select(func.count(PersonCluster.id)).where(
            PersonCluster.user_id == user_id
        )
    )
    total_persons = persons_result.scalar() or 0

    images_processed = 0
    if queue:
        images_processed = queue.stats.images_processed

    return FaceQueueStatus(
        queue_pending=queue.queue.qsize() if queue else 0,
        currently_processing=queue.active_workers if queue else 0,
        total_faces_indexed=total_faces,
        total_images_processed=images_processed,
        total_persons_clustered=total_persons,
        workers_active=queue.active_workers if queue else 0,
        workers_max=queue.max_workers if queue else 0,
        system_cpu_percent=psutil.cpu_percent(interval=0),
        system_ram_percent=psutil.virtual_memory().percent,
    )


# ── Stats for dashboard ──────────────────────────────────────────────

@router.get("/stats/{user_id}")
async def get_face_stats(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Face detection statistics for the dashboard."""
    total_faces = await db.execute(
        select(func.count(FaceEmbedding.id)).where(
            FaceEmbedding.user_id == user_id
        )
    )
    total_persons = await db.execute(
        select(func.count(PersonCluster.id)).where(
            PersonCluster.user_id == user_id
        )
    )
    total_images = await db.execute(
        select(func.count(func.distinct(FaceEmbedding.upload_log_id))).where(
            FaceEmbedding.user_id == user_id
        )
    )

    return {
        "total_faces": total_faces.scalar() or 0,
        "total_persons": total_persons.scalar() or 0,
        "total_images_with_faces": total_images.scalar() or 0,
    }

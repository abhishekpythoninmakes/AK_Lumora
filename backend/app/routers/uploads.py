"""Upload and dashboard statistics routes."""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse, Response
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional

from app.database import get_db
from app.models.upload import UploadLog
from app.models.folder import WatchedFolder, DriveConfig
from app.schemas.upload import (
    UploadLogResponse,
    DashboardStats,
    DashboardChartData,
    UploadRatePoint,
    ResumableUploadRequest,
    ResumableUploadResponse,
    FinalizeUploadRequest,
)
from app.services.drive_service import (
    create_resumable_upload,
    get_drive_credentials,
    make_file_public,
    list_drive_images,
)
from app.websocket import manager

router = APIRouter(prefix="/api/uploads", tags=["Uploads"])


async def _fallback_recent_items(user_id: int, db: AsyncSession, limit: int):
    fallback_query = (
        select(UploadLog, WatchedFolder)
        .join(WatchedFolder, UploadLog.folder_id == WatchedFolder.id)
        .where(
            UploadLog.user_id == user_id,
            UploadLog.status == "completed",
            UploadLog.drive_file_id.isnot(None),
        )
        .order_by(UploadLog.created_at.desc())
        .limit(limit)
    )
    fallback_rows = (await db.execute(fallback_query)).all()
    fallback_items = []
    for log, watched in fallback_rows:
        file_id = log.drive_file_id
        fallback_items.append({
            "id": str(log.id),
            "name": log.file_name,
            "mime_type": (f"image/{(log.file_format or '').lower()}" if log.file_format else "image/*"),
            "size": int((log.file_size_mb or 0) * 1024 * 1024),
            "created_at": log.created_at.isoformat() if log.created_at else None,
            "folder_name": watched.folder_name or "Unknown",
            "drive_folder_name": watched.drive_folder_name,
            "watched_folder_id": watched.id,
            "folder_id": watched.drive_folder_id,
            "thumbnail_url": log.thumbnail_url or (f"https://drive.google.com/thumbnail?id={file_id}&sz=w800" if file_id else None),
            "public_link": log.public_link or (f"https://drive.google.com/uc?export=view&id={file_id}" if file_id else None),
            "drive_file_id": file_id,
        })
    return {"items": fallback_items, "next_page_token": None}


@router.get("/", response_model=list[UploadLogResponse])
async def list_uploads(
    user_id: int,
    folder_id: Optional[int] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List upload logs with filters."""
    query = select(UploadLog, WatchedFolder.folder_name).where(UploadLog.user_id == user_id)

    if folder_id:
        query = query.where(UploadLog.folder_id == folder_id)
    if status:
        query = query.where(UploadLog.status == status)
    if date_from:
        query = query.where(UploadLog.created_at >= datetime.fromisoformat(date_from).replace(tzinfo=None))
    if date_to:
        query = query.where(UploadLog.created_at <= datetime.fromisoformat(date_to).replace(tzinfo=None))

    query = query.order_by(UploadLog.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query.join(WatchedFolder, UploadLog.folder_id == WatchedFolder.id))
    rows = result.all()

    uploads = []
    for upload, folder_name in rows:
        if upload.status != 'completed': continue
        data = UploadLogResponse.model_validate(upload).model_dump()
        data["folder_name"] = folder_name
        uploads.append(data)
    return uploads


@router.get("/drive-files")
async def list_drive_files(
    user_id: int,
    folder_id: Optional[int] = None,
    folder_name: Optional[str] = None,
    drive_config_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    page_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List image files directly from connected Drive folders (not upload_logs)."""
    watched_query = select(WatchedFolder).where(
        WatchedFolder.user_id == user_id,
        WatchedFolder.drive_folder_id.isnot(None),
    )
    if folder_id:
        watched_query = watched_query.where(WatchedFolder.id == folder_id)
    if folder_name:
        watched_query = watched_query.where(WatchedFolder.folder_name == folder_name)
    if drive_config_id:
        watched_query = watched_query.where(WatchedFolder.drive_config_id == drive_config_id)

    watched_rows = (await db.execute(watched_query)).scalars().all()
    if not watched_rows:
        return {"items": [], "next_page_token": None}

    folder_ids = list({w.drive_folder_id for w in watched_rows if w.drive_folder_id})
    folder_name_map = {w.drive_folder_id: w.folder_name for w in watched_rows if w.drive_folder_id}
    drive_folder_name_map = {w.drive_folder_id: w.drive_folder_name for w in watched_rows if w.drive_folder_id}
    watched_folder_id_map = {w.drive_folder_id: w.id for w in watched_rows if w.drive_folder_id}

    # If watched folders exist but none have a Drive folder id, Drive is the source of truth:
    # return empty until configuration is fixed.
    if not folder_ids:
        return {"items": [], "next_page_token": None}

    selected_drive_config_id = drive_config_id
    if not selected_drive_config_id:
        selected_drive_config_id = next((w.drive_config_id for w in watched_rows if w.drive_config_id), None)
    if not selected_drive_config_id:
        active_cfg = (
            await db.execute(
                select(DriveConfig.id).where(
                    DriveConfig.user_id == user_id,
                    DriveConfig.is_active == True,
                )
            )
        ).scalars().first()
        selected_drive_config_id = active_cfg
    if not selected_drive_config_id:
        return {"items": [], "next_page_token": None}

    creds = await get_drive_credentials(db, user_id, selected_drive_config_id)
    if not creds or not creds.get("access_token"):
        return {"items": [], "next_page_token": None}

    drive_result = await list_drive_images(
        access_token=creds["access_token"],
        folder_ids=folder_ids,
        limit=limit,
        page_token=page_token,
        date_from=date_from,
        date_to=date_to,
    )

    items = []
    for file in drive_result.get("files", []):
        file_id = file.get("id")
        parent_id = (file.get("parents") or [None])[0]
        thumbnail_url = file.get("thumbnailLink") or (f"https://drive.google.com/thumbnail?id={file_id}&sz=w800" if file_id else None)
        public_link = file.get("webContentLink") or file.get("webViewLink") or (f"https://drive.google.com/uc?export=view&id={file_id}" if file_id else None)

        items.append({
            "id": file_id,
            "name": file.get("name"),
            "mime_type": file.get("mimeType"),
            "size": int(file.get("size") or 0),
            "created_at": file.get("createdTime"),
            "folder_name": folder_name_map.get(parent_id, "Unknown"),
            "drive_folder_name": drive_folder_name_map.get(parent_id),
            "watched_folder_id": watched_folder_id_map.get(parent_id),
            "folder_id": parent_id,
            "thumbnail_url": thumbnail_url,
            "public_link": public_link,
            "drive_file_id": file_id,
        })

    return {"items": items, "next_page_token": drive_result.get("next_page_token")}


@router.get("/stats", response_model=DashboardChartData)
async def get_dashboard_stats(
    user_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated dashboard statistics."""
    # Default to today
    now = datetime.now(timezone.utc)
    if not date_from:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start = datetime.fromisoformat(date_from)

    if not date_to:
        end = now
    else:
        end = datetime.fromisoformat(date_to)

    # Convert to timezone-naive to avoid asyncpg data errors with TIMESTAMP WITHOUT TIME ZONE
    start = start.replace(tzinfo=None)
    end = end.replace(tzinfo=None)

    base_filter = and_(
        UploadLog.user_id == user_id,
        UploadLog.created_at >= start,
        UploadLog.created_at <= end,
    )

    # Aggregate stats
    total = await db.execute(
        select(func.count(UploadLog.id)).where(base_filter)
    )
    success = await db.execute(
        select(func.count(UploadLog.id)).where(
            base_filter, UploadLog.status == "completed"
        )
    )
    failed = await db.execute(
        select(func.count(UploadLog.id)).where(
            base_filter, UploadLog.status == "failed"
        )
    )
    faces = await db.execute(
        select(func.coalesce(func.sum(UploadLog.faces_detected), 0)).where(base_filter)
    )
    avg_time = await db.execute(
        select(func.coalesce(func.avg(UploadLog.upload_time_sec), 0.0)).where(
            base_filter, UploadLog.status == "completed"
        )
    )
    total_size = await db.execute(
        select(func.coalesce(func.sum(UploadLog.file_size_mb), 0.0)).where(base_filter)
    )

    # Folder stats
    active_folders = await db.execute(
        select(func.count(WatchedFolder.id)).where(
            WatchedFolder.user_id == user_id, WatchedFolder.is_watching == True
        )
    )
    total_folders = await db.execute(
        select(func.count(WatchedFolder.id)).where(WatchedFolder.user_id == user_id)
    )

    stats = DashboardStats(
        total_uploads=total.scalar() or 0,
        successful_uploads=success.scalar() or 0,
        failed_uploads=failed.scalar() or 0,
        total_faces_scanned=faces.scalar() or 0,
        avg_upload_time=round(avg_time.scalar() or 0, 2),
        total_size_mb=round(total_size.scalar() or 0, 2),
        active_folders=active_folders.scalar() or 0,
        total_folders=total_folders.scalar() or 0,
    )

    # Upload rate over time (hourly buckets)
    upload_rate = []
    hours = min(int((end - start).total_seconds() / 3600) + 1, 24)
    for i in range(hours):
        bucket_start = start + timedelta(hours=i)
        bucket_end = bucket_start + timedelta(hours=1)
        count_result = await db.execute(
            select(func.count(UploadLog.id)).where(
                base_filter,
                UploadLog.created_at >= bucket_start,
                UploadLog.created_at < bucket_end,
            )
        )
        size_result = await db.execute(
            select(func.coalesce(func.sum(UploadLog.file_size_mb), 0.0)).where(
                base_filter,
                UploadLog.created_at >= bucket_start,
                UploadLog.created_at < bucket_end,
            )
        )
        upload_rate.append(
            UploadRatePoint(
                timestamp=bucket_start.isoformat(),
                count=count_result.scalar() or 0,
                size_mb=round(size_result.scalar() or 0, 2),
            )
        )

    return DashboardChartData(upload_rate=upload_rate, stats=stats)


@router.post("/resumable", response_model=ResumableUploadResponse)
async def create_resumable(
    request: ResumableUploadRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    """Create a resumable upload URL for direct client-to-Drive upload."""
    # Get the folder's drive folder ID
    result = await db.execute(
        select(WatchedFolder).where(WatchedFolder.id == request.folder_id)
    )
    folder = result.scalar_one_or_none()
    if not folder or not folder.drive_folder_id:
        raise HTTPException(
            status_code=400,
            detail="Folder not configured with Drive target",
        )

    if not folder.drive_config_id:
        raise HTTPException(status_code=400, detail="Drive not configured for this folder")

    creds = await get_drive_credentials(db, folder.user_id, folder.drive_config_id)
    if not creds or not creds.get("access_token"):
        raise HTTPException(status_code=401, detail="Invalid drive credentials")

    upload_url = await create_resumable_upload(
        access_token=creds["access_token"],
        folder_id=folder.drive_folder_id,
        file_name=request.file_name,
        file_size=request.file_size,
        mime_type=request.mime_type,
        origin=req.headers.get("origin", "http://localhost:5173"),
    )
    if not upload_url:
        raise HTTPException(status_code=500, detail="Failed to create upload session")

    return ResumableUploadResponse(
        upload_url=upload_url,
        drive_folder_id=folder.drive_folder_id,
        file_name=request.file_name,
    )


@router.post("/log")
async def log_upload(
    user_id: int,
    folder_id: int,
    file_name: str,
    file_path: str,
    file_format: str = None,
    file_size_mb: float = None,
    drive_file_id: str = None,
    public_link: str = None,
    status_val: str = "pending",
    error_message: str = None,
    upload_time_sec: float = None,
    db: AsyncSession = Depends(get_db),
):
    """Log a file upload event."""
    log = UploadLog(
        user_id=user_id,
        folder_id=folder_id,
        file_name=file_name,
        file_path=file_path,
        file_format=file_format,
        file_size_mb=file_size_mb,
        drive_file_id=drive_file_id,
        public_link=public_link,
        status=status_val,
        error_message=error_message,
        upload_time_sec=upload_time_sec,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return UploadLogResponse.model_validate(log)


@router.post("/finalize", response_model=UploadLogResponse)
async def finalize_upload(
    request: FinalizeUploadRequest,
    db: AsyncSession = Depends(get_db),
):
    """Finalize an upload by making it public and updating the log."""
    # Get the upload log and associated folder
    result = await db.execute(
        select(UploadLog, WatchedFolder)
        .join(WatchedFolder, UploadLog.folder_id == WatchedFolder.id)
        .where(UploadLog.id == request.upload_log_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Upload log not found")
        
    log, folder = row

    if not folder.drive_config_id:
        raise HTTPException(status_code=400, detail="Drive not configured")

    creds = await get_drive_credentials(db, folder.user_id, folder.drive_config_id)
    if not creds or not creds.get("access_token"):
        raise HTTPException(status_code=401, detail="Invalid drive credentials")

    # Backend handles making file public (more reliable than frontend token)
    public_link, thumbnail_link = await make_file_public(creds["access_token"], request.drive_file_id)
    
    # Fallback: use public Drive URL format (works without auth once file is public)
    if not public_link:
        public_link = f"https://drive.google.com/uc?export=view&id={request.drive_file_id}"
    if not thumbnail_link:
        thumbnail_link = f"https://drive.google.com/thumbnail?id={request.drive_file_id}&sz=w800"

    log.drive_file_id = request.drive_file_id
    log.public_link = public_link
    log.thumbnail_url = thumbnail_link
    log.upload_time_sec = request.upload_time_sec
    log.status = "completed"

    await db.commit()
    await db.refresh(log)

    # ── Enqueue for background face-embedding generation ──────
    try:
        from app.services import face_queue as fq_mod
        from app.services.face_queue import FaceTask

        queue = fq_mod.face_queue
        if queue is not None:
            await queue.enqueue(
                FaceTask(
                    upload_log_id=log.id,
                    user_id=log.user_id,
                    folder_id=log.folder_id,
                    file_path=log.file_path,  # typically 'browser://...' or not local
                    drive_file_id=request.drive_file_id,
                )
            )
            import logging
            logging.getLogger(__name__).info("Enqueued browser upload %d for face embedding", log.id)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Failed to enqueue face detection task for finalized upload %d: %s", log.id, e)

    # ── Backfill drive_file_id on face embeddings for this upload ──
    try:
        from app.models.face import FaceEmbedding
        from sqlalchemy import update as sql_update

        await db.execute(
            sql_update(FaceEmbedding)
            .where(FaceEmbedding.upload_log_id == log.id)
            .values(drive_file_id=request.drive_file_id)
        )
        await db.commit()

        # Also update Qdrant payload so searches return drive_file_id
        from app.services import vector_store as vs_mod
        import asyncio

        store = vs_mod.vector_store
        if store:
            fe_result = await db.execute(
                select(FaceEmbedding.id).where(
                    FaceEmbedding.upload_log_id == log.id
                )
            )
            face_ids = [row[0] for row in fe_result.all()]
            for fid in face_ids:
                try:
                    store.set_payload(
                        payload={
                            "drive_file_id": str(request.drive_file_id),
                            "public_link": f"https://drive.google.com/uc?export=view&id={request.drive_file_id}",
                            "thumbnail_url": f"https://drive.google.com/thumbnail?id={request.drive_file_id}&sz=w800",
                        },
                        points=[int(fid)],
                    )
                except Exception:
                    pass
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(
            "Failed to backfill drive_file_id on face embeddings: %s", e
        )

    # Broadcast to all connected clients so Live Studio updates instantly
    message = {
        "type": "upload_completed",
        "upload_log_id": log.id,
        "folder_id": log.folder_id,
        "file_name": log.file_name,
        "drive_file_id": log.drive_file_id,
        "public_link": log.public_link,
        "thumbnail_url": log.thumbnail_url,
        "folder_name": folder.folder_name,
        "file_size": int((log.file_size_mb or 0) * 1024 * 1024),
        "status": log.status,
    }
    await manager.send_to_user(log.user_id, message)

    return UploadLogResponse.model_validate(log)


@router.get("/stream/{upload_log_id}")
async def stream_local_file(upload_log_id: int, db: AsyncSession = Depends(get_db)):
    """Stream a local file directly from the filesystem without copying."""
    result = await db.execute(select(UploadLog).where(UploadLog.id == upload_log_id))
    log = result.scalar_one_or_none()
    if not log or not log.file_path:
        raise HTTPException(status_code=404, detail="File not found")
        
    import os
    if not os.path.exists(log.file_path):
        raise HTTPException(status_code=404, detail="Local file no longer exists")
        
    return FileResponse(
        log.file_path,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@router.get("/public-image/{drive_file_id}")
async def proxy_public_drive_image(drive_file_id: str):
    """Proxy a public Drive image to avoid frontend CORS issues."""
    view_url = f"https://drive.google.com/uc?export=view&id={drive_file_id}"
    thumb_url = f"https://drive.google.com/thumbnail?id={drive_file_id}&sz=w1600"

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.get(view_url)
        if resp.status_code != 200 or "text/html" in (resp.headers.get("content-type", "").lower()):
            resp = await client.get(thumb_url)

        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Unable to fetch public Drive image")

        content_type = resp.headers.get("content-type", "image/jpeg")
        return Response(
            content=resp.content,
            media_type=content_type,
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )


@router.get("/public-thumbnail/{drive_file_id}")
async def proxy_public_drive_thumbnail(drive_file_id: str):
    """Proxy a Drive thumbnail for stable frontend rendering."""
    thumb_url = f"https://drive.google.com/thumbnail?id={drive_file_id}&sz=w800"
    view_url = f"https://drive.google.com/uc?export=view&id={drive_file_id}"

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.get(thumb_url)
        if resp.status_code != 200 or "text/html" in (resp.headers.get("content-type", "").lower()):
            resp = await client.get(view_url)

        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Unable to fetch Drive thumbnail")

        content_type = resp.headers.get("content-type", "image/jpeg")
        return Response(
            content=resp.content,
            media_type=content_type,
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

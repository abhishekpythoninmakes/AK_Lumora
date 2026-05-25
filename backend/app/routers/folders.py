"""Folder management routes — watched folders CRUD and monitoring controls."""

import os
import string
import logging

logger = logging.getLogger(__name__)

# Base directory for managed (cloud-hosted) watched folders.
# In production this resolves to a path inside the Railway container.
MANAGED_FOLDERS_ROOT = os.path.abspath(
    os.getenv("MANAGED_FOLDERS_ROOT", os.path.join("uploads", "watched"))
)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.folder import WatchedFolder
from app.schemas.folder import FolderCreateRequest, FolderResponse
from app.services.file_monitor import file_monitor
from app.services.drive_service import (
    get_drive_credentials,
    create_drive_folder,
    list_drive_folders
)

router = APIRouter(prefix="/api/folders", tags=["Folders"])

MAX_FOLDERS = 20


@router.get("/browse")
async def browse_directory(path: str = ""):
    """Browse local filesystem directories for folder selection."""
    if not path:
        # Return drive letters on Windows, or root on Unix
        if os.name == "nt":
            drives = []
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(
                        {"name": f"{letter}:", "path": f"{letter}:/", "is_dir": True}
                    )
            return {"current": "", "parent": "", "directories": drives}
        else:
            path = "/"

    # Normalize path for the OS
    normalized = os.path.normpath(path)
    if not os.path.exists(normalized):
        raise HTTPException(status_code=404, detail="Path not found")
    if not os.path.isdir(normalized):
        raise HTTPException(status_code=400, detail="Path is not a directory")

    parent = os.path.dirname(normalized)
    if parent == normalized:
        parent = ""  # We're at root

    directories = []
    try:
        for entry in os.scandir(normalized):
            if entry.is_dir() and not entry.name.startswith("."):
                try:
                    directories.append(
                        {
                            "name": entry.name,
                            "path": entry.path.replace("\\", "/"),
                            "is_dir": True,
                        }
                    )
                except PermissionError:
                    pass
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")

    directories.sort(key=lambda x: x["name"].lower())
    return {
        "current": normalized.replace("\\", "/"),
        "parent": parent.replace("\\", "/") if parent else "",
        "directories": directories,
    }


@router.get("/drive-folders")
async def get_drive_folders_endpoint(user_id: int, drive_config_id: int, db: AsyncSession = Depends(get_db)):
    """List folders from the selected Google Drive account."""
    creds = await get_drive_credentials(db, user_id, drive_config_id=drive_config_id)
    if not creds or not creds.get("access_token"):
        raise HTTPException(status_code=400, detail="Drive credentials not found")
    folders = await list_drive_folders(creds["access_token"])
    return folders


@router.get("/", response_model=list[FolderResponse])
async def list_folders(user_id: int, db: AsyncSession = Depends(get_db)):
    """List all watched folders for a user."""
    result = await db.execute(
        select(WatchedFolder)
        .where(WatchedFolder.user_id == user_id)
        .order_by(WatchedFolder.created_at.desc())
    )
    folders = result.scalars().all()
    return [FolderResponse.model_validate(f) for f in folders]


@router.post("/", response_model=FolderResponse)
async def create_folder(
    request: FolderCreateRequest,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Add a new folder to watch (max 20) and create Drive folder if needed."""
    # Check folder count
    count_result = await db.execute(
        select(func.count(WatchedFolder.id)).where(WatchedFolder.user_id == user_id)
    )
    count = count_result.scalar()
    if count >= MAX_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum of {MAX_FOLDERS} folders allowed",
        )

    if not request.drive_config_id:
        raise HTTPException(
            status_code=400,
            detail="Drive configuration is required to bind a watched folder to Google Drive.",
        )

    folder_path = os.path.normpath(request.local_path)
    drive_folder_id = request.drive_folder_id

    # Always fetch/verify Google Drive credentials to ensure they are valid
    creds = await get_drive_credentials(db, user_id, drive_config_id=request.drive_config_id)
    if not creds or not creds.get("access_token"):
        raise HTTPException(
            status_code=400,
            detail="Google Drive credentials not found or expired. Please connect your Google Drive account first.",
        )

    if not drive_folder_id and request.drive_folder_name:
        # Check if a folder with this name already exists
        existing_folders = await list_drive_folders(creds["access_token"])
        found = next((f for f in existing_folders if f["name"] == request.drive_folder_name), None)
        
        if found:
            drive_folder_id = found["id"]
        else:
            drive_res = await create_drive_folder(creds["access_token"], request.drive_folder_name)
            # If the Drive API returned an error payload, surface it to the client
            if drive_res is None:
                # unexpected None — treat as generic failure
                raise HTTPException(status_code=500, detail="Failed to create Drive folder")
            if isinstance(drive_res, dict) and drive_res.get("error"):
                raise HTTPException(status_code=502, detail={"drive_error": drive_res.get("error"), "status": drive_res.get("status_code")})
            if drive_res and "id" in drive_res:
                drive_folder_id = drive_res["id"]

    if not drive_folder_id:
        raise HTTPException(
            status_code=400,
            detail="Failed to resolve or create a valid Google Drive target folder. Please check your Drive account and try again.",
        )

    folder = WatchedFolder(
        user_id=user_id,
        local_path=folder_path,
        folder_name=request.folder_name,
        drive_folder_name=request.drive_folder_name,
        drive_folder_id=drive_folder_id,
        drive_config_id=request.drive_config_id,
    )
    db.add(folder)
    await db.flush()

    # If the local path doesn't exist on this server (i.e. cloud deployment),
    # use a managed directory so watchdog can still monitor for uploaded files.
    effective_path = folder.local_path
    if not os.path.isdir(effective_path):
        managed_path = os.path.join(MANAGED_FOLDERS_ROOT, str(folder.id))
        os.makedirs(managed_path, exist_ok=True)
        effective_path = managed_path
        logger.info(f"Cloud mode: remapped folder {folder.id} to managed path {managed_path} (in-memory)")

    folder.is_watching = file_monitor.start_watching(folder.id, effective_path)

    await db.refresh(folder)
    return FolderResponse.model_validate(folder)


@router.delete("/{folder_id}")
async def delete_folder(folder_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    """Remove a watched folder."""
    result = await db.execute(
        select(WatchedFolder).where(
            WatchedFolder.id == folder_id, WatchedFolder.user_id == user_id
        )
    )
    folder = result.scalar_one_or_none()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Stop monitoring if active
    file_monitor.stop_watching(folder_id)

    await db.delete(folder)
    return {"status": "deleted"}


@router.post("/{folder_id}/start")
async def start_watching(folder_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    """Start monitoring a folder for new images."""
    result = await db.execute(
        select(WatchedFolder).where(
            WatchedFolder.id == folder_id, WatchedFolder.user_id == user_id
        )
    )
    folder = result.scalar_one_or_none()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    folder_path = os.path.normpath(folder.local_path)

    # If the stored path doesn't exist on this host (cloud deployment),
    # use a managed server-side directory for this folder.
    if not os.path.isdir(folder_path):
        managed_path = os.path.join(MANAGED_FOLDERS_ROOT, str(folder_id))
        os.makedirs(managed_path, exist_ok=True)
        folder_path = managed_path
        logger.info(
            f"Cloud mode: using managed folder path {managed_path} for watcher (in-memory)"
        )

    success = file_monitor.start_watching(folder_id, folder_path)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to start monitoring. Check if the folder path exists.",
        )

    folder.is_watching = True
    await db.flush()
    return {"status": "watching", "folder_id": folder_id}


@router.post("/{folder_id}/stop")
async def stop_watching(folder_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    """Stop monitoring a folder."""
    result = await db.execute(
        select(WatchedFolder).where(
            WatchedFolder.id == folder_id, WatchedFolder.user_id == user_id
        )
    )
    folder = result.scalar_one_or_none()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    file_monitor.stop_watching(folder_id)
    folder.is_watching = False
    await db.flush()
    return {"status": "stopped", "folder_id": folder_id}

"""Google Drive service — handles Drive API operations."""

import os
import time
import mimetypes
import asyncio
import httpx
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.folder import DriveConfig
from app.config import settings
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import google.auth.transport.requests

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]


async def refresh_google_credentials(creds: Credentials, db: AsyncSession, config: DriveConfig) -> Credentials:
    """Refresh OAuth credentials using the stored refresh token."""
    if creds.refresh_token and not creds.valid:
        request = google.auth.transport.requests.Request()
        await asyncio.to_thread(creds.refresh, request)
        config.access_token = creds.token
        config.token_expiry = creds.expiry.replace(tzinfo=None) if creds.expiry else None
        await db.commit()
    return creds


async def get_drive_credentials(db: AsyncSession, user_id: int, drive_config_id: Optional[int] = None) -> Optional[dict]:
    """Get stored Drive credentials for a user and refresh them if needed."""
    query = select(DriveConfig).where(DriveConfig.user_id == user_id)
    if drive_config_id:
        query = query.where(DriveConfig.id == drive_config_id)
    else:
        query = query.where(DriveConfig.is_active == True)

    result = await db.execute(query)
    config = result.scalars().first()
    if not config:
        return None

    creds = Credentials(
        token=config.access_token,
        refresh_token=config.refresh_token,
        client_id=settings.GOOGLE_DRIVE_CLIENT_ID,
        client_secret=settings.GOOGLE_DRIVE_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
        expiry=config.token_expiry,
    )

    import logging
    logger = logging.getLogger(__name__)

    should_refresh = False
    if creds.refresh_token:
        if not creds.valid or not config.token_expiry:
            should_refresh = True
        elif config.token_expiry and config.token_expiry.tzinfo is None:
            # treat naive dt as UTC
            expiry_utc = config.token_expiry.replace(tzinfo=timezone.utc)
            if expiry_utc <= datetime.now(timezone.utc) + timedelta(minutes=5):
                should_refresh = True
        elif config.token_expiry and config.token_expiry <= datetime.now(timezone.utc) + timedelta(minutes=5):
            should_refresh = True

    if should_refresh and creds.refresh_token:
        try:
            creds = await refresh_google_credentials(creds, db, config)
        except Exception as e:
            logger.error(f"Failed to refresh Drive token: {e}")

    return {
        "client_id": settings.GOOGLE_DRIVE_CLIENT_ID,
        "client_secret": settings.GOOGLE_DRIVE_CLIENT_SECRET,
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
    }

def get_global_oauth_flow(redirect_uri: str) -> Flow:
    from app.config import settings
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_DRIVE_CLIENT_ID,
            "client_secret": settings.GOOGLE_DRIVE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    return Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )

async def get_oauth_flow(db: AsyncSession, user_id: int, redirect_uri: str) -> Optional[Flow]:
    """Create a Google OAuth Flow object from stored credentials."""
    return get_global_oauth_flow(redirect_uri)


async def test_drive_connection(access_token: str) -> dict:
    """Test Google Drive connectivity by fetching user and storage info."""
    url = "https://www.googleapis.com/drive/v3/about?fields=user,storageQuota"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            return {"success": False, "error": resp.text}
        return {"success": True, "data": resp.json()}


async def get_drive_account_status(access_token: str) -> dict:
    """Return a normalized Drive account status payload."""
    result = await test_drive_connection(access_token)
    if not result.get("success"):
        return {"success": False, "error": result.get("error")}

    data = result["data"]
    quota = data.get("storageQuota", {})
    used = int(quota.get("usage", 0))
    total = int(quota.get("limit", 0))
    free = total - used if total > used else 0
    return {
        "success": True,
        "storage": {
            "used_bytes": used,
            "total_bytes": total,
            "free_bytes": free,
        },
        "user": data.get("user", {}),
    }


async def list_drive_folders(access_token: str) -> List[dict]:
    """List folders in Google Drive using a simple files.list style query."""
    base_url = "https://www.googleapis.com/drive/v3/files"
    headers = {"Authorization": f"Bearer {access_token}"}
    query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"

    folders: List[dict] = []
    page_token: Optional[str] = None

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            params = {
                "q": query,
                "fields": "nextPageToken, files(id, name, createdTime, parents)",
                "pageSize": 1000,
                "orderBy": "name",
            }
            if page_token:
                params["pageToken"] = page_token

            resp = await client.get(base_url, headers=headers, params=params)
            if resp.status_code != 200:
                return []

            data = resp.json()
            folders.extend(data.get("files", []))
            page_token = data.get("nextPageToken")
            if not page_token:
                break

    return folders


async def list_drive_images(
    access_token: str,
    folder_ids: Optional[List[str]] = None,
    limit: int = 10,
    page_token: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """List image files from Google Drive with pagination and optional filters."""
    filters = [
        "trashed=false",
        "mimeType contains 'image/'",
    ]
    if folder_ids:
        parent_filters = " or ".join([f"'{folder_id}' in parents" for folder_id in folder_ids if folder_id])
        if parent_filters:
            filters.append(f"({parent_filters})")
    if date_from:
        filters.append(f"createdTime >= '{date_from}'")
    if date_to:
        filters.append(f"createdTime <= '{date_to}'")

    q = " and ".join(filters)
    url = "https://www.googleapis.com/drive/v3/files"
    params = {
        "q": q,
        "fields": "nextPageToken,files(id,name,mimeType,size,createdTime,thumbnailLink,webViewLink,webContentLink,parents,imageMediaMetadata)",
        "orderBy": "createdTime desc",
        "pageSize": max(1, min(limit, 100)),
        "supportsAllDrives": "true",
        "includeItemsFromAllDrives": "true",
    }
    if page_token:
        params["pageToken"] = page_token

    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            return {"files": [], "next_page_token": None}
        data = resp.json()
        return {
            "files": data.get("files", []),
            "next_page_token": data.get("nextPageToken"),
        }


async def create_drive_folder(access_token: str, folder_name: str) -> Optional[dict]:
    """Create a folder in Google Drive root."""
    url = "https://www.googleapis.com/drive/v3/files"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    body = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=body)
        # Return JSON on success, otherwise include error details for debugging
        if resp.status_code in (200, 201):
            return resp.json()
        try:
            error_payload = resp.json()
        except Exception:
            error_payload = {"text": resp.text}
        return {"error": error_payload, "status_code": resp.status_code}


async def create_resumable_upload(
    access_token: str, folder_id: str, file_name: str, file_size: int, mime_type: str, origin: str = "http://localhost:5173"
) -> Optional[str]:
    """Create a resumable upload session and return the upload URI."""
    url = (
        "https://www.googleapis.com/upload/drive/v3/files"
        "?uploadType=resumable&fields=id,name,webViewLink,webContentLink"
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": mime_type,
        "X-Upload-Content-Length": str(file_size),
        "Origin": origin,
    }
    body = {
        "name": file_name,
        "parents": [folder_id],
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, headers=headers, json=body)
        if resp.status_code in (200, 201):
            return resp.headers.get("Location")
        return None


async def upload_file_to_resumable_session(upload_url: str, file_path: str, mime_type: str) -> Optional[dict]:
    """Upload file data to a resumable Drive upload session."""
    file_size = os.path.getsize(file_path)
    headers = {
        "Content-Type": mime_type,
        "Content-Length": str(file_size),
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        with open(file_path, "rb") as file_stream:
            resp = await client.put(upload_url, headers=headers, content=file_stream)
            if resp.status_code in (200, 201):
                return resp.json()
    return None


async def make_file_public(access_token: str, file_id: str) -> tuple[Optional[str], Optional[str]]:
    """Make a Drive file publicly accessible and return the (download_link, thumbnail_link)."""
    perm_url = f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        post_resp = await client.post(
            perm_url,
            headers=headers,
            json={"role": "reader", "type": "anyone"},
        )
        if post_resp.status_code not in (200, 201):
            import logging
            logging.error(f"make_file_public POST failed: {post_resp.status_code} - {post_resp.text}")

        file_url = (
            f"https://www.googleapis.com/drive/v3/files/{file_id}"
            f"?fields=webViewLink,webContentLink,thumbnailLink"
        )
        resp = await client.get(file_url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            public_link = data.get("webContentLink") or data.get("webViewLink")
            thumbnail_link = data.get("thumbnailLink")
            return public_link, thumbnail_link
        else:
            import logging
            logging.error(f"make_file_public GET failed: {resp.status_code} - {resp.text}")
            
    return None, None


async def upload_image_to_drive(access_token: str, folder_id: str, file_path: str) -> Optional[dict]:
    """Upload a local image file to Google Drive using a resumable session."""
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    upload_url = await create_resumable_upload(
        access_token=access_token,
        folder_id=folder_id,
        file_name=file_name,
        file_size=file_size,
        mime_type=mime_type,
    )
    if not upload_url:
        return None

    file_meta = await upload_file_to_resumable_session(upload_url, file_path, mime_type)
    if not file_meta or not file_meta.get("id"):
        return None

    public_link = await make_file_public(access_token, file_meta["id"])
    return {
        "drive_file_id": file_meta["id"],
        "public_link": public_link,
        "file_size": file_size,
        "mime_type": mime_type,
        "metadata": file_meta,
    }


async def get_preview_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=view&id={file_id}"


async def download_drive_file(db: AsyncSession, user_id: int, drive_file_id: str, drive_config_id: Optional[int] = None) -> Optional[bytes]:
    """Download a file's content from Google Drive in-memory using oauth token."""
    import logging
    logger = logging.getLogger(__name__)

    creds = await get_drive_credentials(db, user_id, drive_config_id=drive_config_id)
    if not creds or not creds.get("access_token"):
        logger.error("download_drive_file: credentials unavailable for user %d", user_id)
        return None

    url = f"https://www.googleapis.com/drive/v3/files/{drive_file_id}?alt=media"
    headers = {"Authorization": f"Bearer {creds['access_token']}"}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.content
            logger.error("download_drive_file failed for %s: %d - %s", drive_file_id, resp.status_code, resp.text)
    except Exception as exc:
        logger.error("download_drive_file exception for %s: %s", drive_file_id, exc)

    return None

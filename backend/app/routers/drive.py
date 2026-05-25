"""Google Drive configuration routes."""

import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.database import get_db
from app.models.folder import DriveConfig
from app.models.user import User
from app.schemas.folder import DriveConfigRequest, DriveConfigResponse, DriveConfigUpdateRequest
from app.services.drive_service import (
    test_drive_connection,
    list_drive_folders,
    create_drive_folder,
    get_global_oauth_flow,
    get_drive_credentials,
    get_drive_account_status,
)

router = APIRouter(prefix="/api/drive", tags=["Google Drive"])


async def fetch_google_user_email(access_token: str) -> str | None:
    """Fetch user email from Google userinfo endpoint."""
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"})
        if resp.status_code == 200:
            return resp.json().get("email")
    return None


@router.get("/auth-url")
async def get_auth_url(redirect_uri: str):
    """Generate Google OAuth authorization URL."""
    flow = get_global_oauth_flow(redirect_uri)
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    code_verifier = getattr(flow, "code_verifier", None)
    return {"auth_url": auth_url, "state": state, "code_verifier": code_verifier}


@router.post("/callback")
async def oauth_callback(
    user_id: int = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    code_verifier: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle OAuth callback to exchange code for tokens."""
    flow = get_global_oauth_flow(redirect_uri)
    if code_verifier:
        flow.code_verifier = code_verifier

    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Get user email
        account_email = await fetch_google_user_email(credentials.token) or "Unknown Account"

        # Update config with tokens
        result = await db.execute(
            select(DriveConfig).where(
                DriveConfig.user_id == user_id, DriveConfig.account_email == account_email
            )
        )
        config = result.scalar_one_or_none()
        if not config:
            config = DriveConfig(user_id=user_id, account_email=account_email, is_active=True)
            db.add(config)
        else:
            config.is_active = True
            
        config.access_token = credentials.token
        config.refresh_token = credentials.refresh_token or config.refresh_token
        config.token_expiry = credentials.expiry.replace(tzinfo=None) if credentials.expiry else None
        
        # Update user flag
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user:
            user.drive_configured = True
            
        await db.commit()
        return {"success": True, "message": "Successfully authenticated with Google Drive"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to authenticate: {str(e)}")


@router.get("/token")
async def get_drive_token(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get the current valid access token for frontend use."""
    creds = await get_drive_credentials(db, user_id)
    if not creds or not creds.get("access_token"):
        raise HTTPException(status_code=401, detail="Google Drive not connected")
    return {"access_token": creds["access_token"]}


@router.get("/accounts")
async def list_accounts(user_id: int, db: AsyncSession = Depends(get_db)):
    """List all connected Google Drive accounts for a user."""
    result = await db.execute(select(DriveConfig).where(DriveConfig.user_id == user_id, DriveConfig.is_active == True))
    configs = result.scalars().all()

    accounts = []
    for config in configs:
        creds = await get_drive_credentials(db, user_id, drive_config_id=config.id)
        status = {"success": False, "error": "Drive credentials unavailable", "user": {}}
        if creds and creds.get("access_token"):
            status = await get_drive_account_status(creds["access_token"])

        # Prefer stored account_email, otherwise try to extract from Drive 'user' info
        email = config.account_email
        if (not email or email.strip() == "" or email == "Unknown Account") and status.get("user"):
            user_info = status.get("user") or {}
            # Drive may return 'emailAddress' or 'email'
            email = user_info.get("emailAddress") or user_info.get("email") or email
        if (not email or email == "Unknown Account") and creds and creds.get("access_token"):
            email = await fetch_google_user_email(creds["access_token"]) or email

        storage = status.get("storage") if status.get("success") else None
        if email == "Unknown Account" and not status.get("success", False):
            # Hide stale/invalid unknown rows from user-facing account pickers.
            continue

        storage = storage or {}
        total = storage.get("total_bytes", 0) or 0
        used = storage.get("used_bytes", 0) or 0
        usage_percent = round((used / total) * 100, 2) if total > 0 else 0
        if usage_percent >= 95:
            usage_alert = "critical"
        elif usage_percent >= 85:
            usage_alert = "warning"
        else:
            usage_alert = "ok"

        accounts.append(
            {
                "id": config.id,
                "email": email or "Unknown Account",
                "domain": (email.split("@")[-1] if email and "@" in email else None),
                "active": config.is_active,
                "storage": storage,
                "connected": status.get("success", False),
                "error": status.get("error"),
                "usage_percent": usage_percent,
                "usage_alert": usage_alert,
                "cleanup_enabled": config.cleanup_enabled,
                "cleanup_keep_count": config.cleanup_keep_count,
                "compression_quality": config.compression_quality,
            }
        )
    accounts.sort(key=lambda a: (not a.get("connected", False), a.get("email", "")))
    return accounts


@router.get("/status")
async def get_drive_status(user_id: int, drive_config_id: int, db: AsyncSession = Depends(get_db)):
    """Get the selected Google Drive account status and available folders."""
    result = await db.execute(
        select(DriveConfig).where(
            DriveConfig.user_id == user_id, DriveConfig.id == drive_config_id, DriveConfig.is_active == True
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Drive account not found")

    creds = await get_drive_credentials(db, user_id, drive_config_id=drive_config_id)
    if not creds or not creds.get("access_token"):
        raise HTTPException(status_code=400, detail="Drive credentials are unavailable or expired")

    status = await get_drive_account_status(creds["access_token"])
    folders = await list_drive_folders(creds["access_token"])

    storage = status.get("storage", {}) or {}
    total = storage.get("total_bytes", 0) or 0
    used = storage.get("used_bytes", 0) or 0
    usage_percent = round((used / total) * 100, 2) if total > 0 else 0

    return {
        "id": config.id,
        "email": config.account_email,
        "storage": storage,
        "connected": status.get("success", False),
        "error": status.get("error"),
        "folders": folders,
        "usage_percent": usage_percent,
        "cleanup_enabled": config.cleanup_enabled,
        "cleanup_keep_count": config.cleanup_keep_count,
        "compression_quality": config.compression_quality,
    }


@router.post("/test-connection")
async def test_connection(user_id: int, access_token: str, db: AsyncSession = Depends(get_db)):
    """Test Drive connectivity using the provided access token."""
    result = await test_drive_connection(access_token)
    return result


@router.get("/folders")
async def get_drive_folders(access_token: str):
    """List folders in the user's Google Drive."""
    folders = await list_drive_folders(access_token)
    return {"folders": folders}


@router.post("/folders")
async def create_folder(folder_name: str, access_token: str):
    """Create a new folder in Google Drive."""
    folder = await create_drive_folder(access_token, folder_name)
    if not folder:
        raise HTTPException(status_code=500, detail="Failed to create folder")
    return folder


@router.get("/config/{user_id}", response_model=DriveConfigResponse)
async def get_drive_config(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get the active Drive configuration for a user."""
    result = await db.execute(
        select(DriveConfig).where(
            DriveConfig.user_id == user_id, DriveConfig.is_active == True
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="No Drive configuration found")
    return DriveConfigResponse.model_validate(config)


@router.put("/config/{drive_config_id}", response_model=DriveConfigResponse)
async def update_drive_config(
    drive_config_id: int,
    request: DriveConfigUpdateRequest,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Update active Google Drive configuration rolling cleanup settings."""
    result = await db.execute(
        select(DriveConfig).where(
            DriveConfig.id == drive_config_id, DriveConfig.user_id == user_id, DriveConfig.is_active == True
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Drive configuration not found")
        
    if request.cleanup_enabled is not None:
        config.cleanup_enabled = request.cleanup_enabled
    if request.cleanup_keep_count is not None:
        config.cleanup_keep_count = request.cleanup_keep_count
    if request.compression_quality is not None:
        config.compression_quality = request.compression_quality
        
    await db.flush()
    return DriveConfigResponse.model_validate(config)

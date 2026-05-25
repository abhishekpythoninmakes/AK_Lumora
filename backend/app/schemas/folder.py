"""Pydantic schemas for folder and drive configuration."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DriveConfigRequest(BaseModel):
    """Drive configuration input — either client_id + secret or JSON contents."""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    client_secret_json: Optional[str] = None  # Full JSON string from uploaded file


class DriveConfigResponse(BaseModel):
    id: int
    client_id: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FolderCreateRequest(BaseModel):
    """Create a new watched folder."""
    local_path: str
    folder_name: str
    drive_folder_name: str
    drive_folder_id: Optional[str] = None
    drive_config_id: Optional[int] = None


class FolderUpdateRequest(BaseModel):
    """Update watched folder configuration."""
    drive_folder_name: Optional[str] = None
    is_watching: Optional[bool] = None


class FolderResponse(BaseModel):
    id: int
    local_path: str
    folder_name: str
    drive_folder_id: Optional[str] = None
    drive_folder_name: Optional[str] = None
    is_watching: bool
    created_at: datetime

    class Config:
        from_attributes = True

"""Drive configuration and watched folder models."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from app.database import Base


class DriveConfig(Base):
    __tablename__ = "drive_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    client_id = Column(String(500), nullable=True)
    client_secret = Column(String(500), nullable=True)
    client_secret_json = Column(Text, nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    account_email = Column(String(255), nullable=True)
    
    # Automatic Cleanup Settings
    cleanup_enabled = Column(Boolean, default=False)
    cleanup_keep_count = Column(Integer, default=50)

    # Image Upload Compression Quality (percentage value, e.g. 88)
    compression_quality = Column(Integer, default=88)

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False
    )


class WatchedFolder(Base):
    __tablename__ = "watched_folders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    local_path = Column(String(1000), nullable=False)
    folder_name = Column(String(255), nullable=False)
    drive_folder_id = Column(String(255), nullable=True)
    drive_folder_name = Column(String(255), nullable=True)
    drive_config_id = Column(Integer, ForeignKey("drive_configs.id"), nullable=True)
    is_watching = Column(Boolean, default=False)
    
    # Folder-specific Cleanup Settings
    cleanup_enabled = Column(Boolean, default=False)
    cleanup_keep_count = Column(Integer, default=50)

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False
    )

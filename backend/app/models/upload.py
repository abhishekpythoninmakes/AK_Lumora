"""Upload log model for tracking file uploads to Google Drive."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from app.database import Base


class UploadLog(Base):
    __tablename__ = "upload_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    folder_id = Column(
        Integer, ForeignKey("watched_folders.id"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_format = Column(String(50), nullable=True)
    file_size_mb = Column(Float, nullable=True)
    
    # Storage mapping
    preview_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    drive_file_id = Column(String, nullable=True)
    public_link = Column(String(1000), nullable=True)
    qr_code_data = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, uploading, completed, failed
    error_message = Column(Text, nullable=True)
    upload_time_sec = Column(Float, nullable=True)
    faces_detected = Column(Integer, default=0)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False
    )

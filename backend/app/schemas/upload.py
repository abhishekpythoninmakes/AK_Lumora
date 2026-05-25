"""Pydantic schemas for upload logs and dashboard stats."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UploadLogResponse(BaseModel):
    id: int
    folder_id: int
    folder_name: Optional[str] = None
    file_name: str
    file_format: Optional[str] = None
    file_size_mb: Optional[float] = None
    preview_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    drive_file_id: Optional[str] = None
    public_link: Optional[str] = None
    qr_code_data: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    upload_time_sec: Optional[float] = None
    faces_detected: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Aggregated stats for dashboard charts."""
    total_uploads: int = 0
    successful_uploads: int = 0
    failed_uploads: int = 0
    total_faces_scanned: int = 0
    avg_upload_time: float = 0.0
    total_size_mb: float = 0.0
    active_folders: int = 0
    total_folders: int = 0


class UploadRatePoint(BaseModel):
    timestamp: str
    count: int
    size_mb: float


class DashboardChartData(BaseModel):
    upload_rate: List[UploadRatePoint] = []
    stats: DashboardStats = DashboardStats()


class ResumableUploadRequest(BaseModel):
    file_name: str
    file_size: int
    mime_type: str
    folder_id: int


from typing import List, Optional

class ResumableUploadResponse(BaseModel):
    upload_url: str
    drive_folder_id: str
    file_name: str

class FinalizeUploadRequest(BaseModel):
    upload_log_id: int
    drive_file_id: str
    upload_time_sec: float
    public_link: Optional[str] = None
    thumbnail_url: Optional[str] = None

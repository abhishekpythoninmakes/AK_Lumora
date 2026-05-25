"""Pydantic schemas for face search API."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FaceSearchBase64Request(BaseModel):
    """Search by base64-encoded image (camera capture)."""
    image_base64: str
    user_id: int
    threshold: float = Field(default=0.45, ge=0.1, le=1.0)
    limit: int = Field(default=50, ge=1, le=200)
    folder_ids: Optional[List[int]] = None  # filter to specific folders


class FaceSearchResult(BaseModel):
    """A single matching photo."""
    face_embedding_id: int
    upload_log_id: int
    drive_file_id: Optional[str] = None
    similarity: float
    confidence: float = 0.0
    person_id: Optional[int] = None
    folder_id: int
    folder_name: Optional[str] = None
    drive_folder_name: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[float] = None
    public_link: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: Optional[datetime] = None


class FaceSearchResponse(BaseModel):
    """Response from face search."""
    face_detected: bool = False
    face_count: int = 0
    matches: List[FaceSearchResult] = []
    total_matches: int = 0
    threshold_used: float = 0.45
    search_time_ms: float = 0.0


class FaceQueueStatus(BaseModel):
    """Status of the background face processing queue."""
    queue_pending: int = 0
    currently_processing: int = 0
    total_faces_indexed: int = 0
    total_images_processed: int = 0
    total_persons_clustered: int = 0
    workers_active: int = 0
    workers_max: int = 0
    system_cpu_percent: float = 0.0
    system_ram_percent: float = 0.0


class FaceEmbeddingResponse(BaseModel):
    """Face embedding metadata for dashboard."""
    id: int
    upload_log_id: int
    face_index: int
    person_id: Optional[int] = None
    confidence: Optional[float] = None
    drive_file_id: Optional[str] = None
    embedding_stored: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

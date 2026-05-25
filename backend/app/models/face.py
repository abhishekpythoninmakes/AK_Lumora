"""Face embedding and person cluster models for face recognition."""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from app.database import Base


class FaceEmbedding(Base):
    """One row per detected face in an uploaded image."""
    __tablename__ = "face_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    upload_log_id = Column(
        Integer, ForeignKey("upload_logs.id"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    folder_id = Column(
        Integer, ForeignKey("watched_folders.id"), nullable=False, index=True
    )

    # Face metadata
    face_index = Column(Integer, nullable=False, default=0)  # which face in image
    person_id = Column(Integer, nullable=True, index=True)   # assigned after clustering
    bbox_json = Column(Text, nullable=True)       # "[x1, y1, x2, y2]"
    confidence = Column(Float, nullable=True)      # detection confidence
    drive_file_id = Column(String(255), nullable=True, index=True)  # for fast lookup

    # Processing status
    embedding_stored = Column(Boolean, default=False)  # whether Qdrant has this

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False
    )


class PersonCluster(Base):
    """One row per identified person (cluster of same faces)."""
    __tablename__ = "person_clusters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Cluster data
    centroid_json = Column(Text, nullable=True)   # cluster centroid embedding as JSON
    face_count = Column(Integer, default=0)        # number of faces in cluster
    label = Column(String(255), nullable=True)     # optional human-readable label

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )

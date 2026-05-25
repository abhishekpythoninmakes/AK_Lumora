"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings from environment."""

    # App
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./ak_lumora.db"
    )

    # Firebase
    FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_AUTH_DOMAIN: str = os.getenv("FIREBASE_AUTH_DOMAIN", "")
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_STORAGE_BUCKET: str = os.getenv("FIREBASE_STORAGE_BUCKET", "")

    # Google Drive defaults
    GOOGLE_DRIVE_CLIENT_ID: str = os.getenv("GOOGLE_DRIVE_CLIENT_ID", "")
    GOOGLE_DRIVE_CLIENT_SECRET: str = os.getenv("GOOGLE_DRIVE_CLIENT_SECRET", "")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    # Face Detection
    QDRANT_STORAGE_PATH: str = os.getenv("QDRANT_STORAGE_PATH", "./qdrant_data")
    FACE_SIMILARITY_THRESHOLD: float = float(
        os.getenv("FACE_SIMILARITY_THRESHOLD", "0.45")
    )
    FACE_CLUSTER_INTERVAL: int = int(os.getenv("FACE_CLUSTER_INTERVAL", "50"))
    FACE_MAX_WORKERS: int = int(os.getenv("FACE_MAX_WORKERS", "0"))  # 0 = auto
    FACE_MODEL_PREFERENCE: str = os.getenv(
        "FACE_MODEL_PREFERENCE", "auto"
    )  # auto | large | small

    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")


settings = Settings()
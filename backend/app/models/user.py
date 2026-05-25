"""User database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    firebase_uid = Column(String(128), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    studio_name = Column(String(255), nullable=True)
    profile_image = Column(String(500), nullable=True)
    phone_number = Column(String(20), nullable=True)
    country_code = Column(String(10), nullable=True)
    display_name = Column(String(255), nullable=True)
    instagram_link = Column(String(500), nullable=True)
    facebook_link = Column(String(500), nullable=True)
    address = Column(String(500), nullable=True)
    contact_numbers = Column(String(500), nullable=True)
    website_link = Column(String(500), nullable=True)
    whatsapp_number = Column(String(30), nullable=True)
    bio = Column(String(1000), nullable=True)

    @property
    def name(self):
        return self.display_name

    @property
    def phone(self):
        return self.phone_number

    # Flags
    profile_completed = Column(Boolean, default=False)
    drive_configured = Column(Boolean, default=False)
    first_login_tutorial = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )

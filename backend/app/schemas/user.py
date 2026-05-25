"""Pydantic schemas for user-related requests and responses."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FirebaseLoginRequest(BaseModel):
    """Firebase ID token sent after Google auth."""
    id_token: str


class CompleteProfileRequest(BaseModel):
    """Complete studio profile after initial auth."""
    studio_name: str
    phone_number: str
    country_code: str
    profile_image: Optional[str] = None


class UserResponse(BaseModel):
    """User data returned to frontend."""
    id: int
    email: str
    firebase_uid: str
    studio_name: Optional[str] = None
    profile_image: Optional[str] = None
    phone_number: Optional[str] = None
    country_code: Optional[str] = None
    display_name: Optional[str] = None
    instagram_link: Optional[str] = None
    facebook_link: Optional[str] = None
    address: Optional[str] = None
    contact_numbers: Optional[str] = None
    website_link: Optional[str] = None
    whatsapp_number: Optional[str] = None
    bio: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    profile_completed: bool = False
    drive_configured: bool = False
    first_login_tutorial: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

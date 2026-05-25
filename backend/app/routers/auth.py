"""Authentication routes — Firebase login, profile completion, and JWT management."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.schemas.user import (
    FirebaseLoginRequest,
    CompleteProfileRequest,
    UserResponse,
    TokenResponse,
)
from app.services.firebase_auth import verify_firebase_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    token: str = Depends(lambda: None), db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to extract the current user from JWT token."""
    # This will be called via header extraction in the actual implementation
    pass


@router.post("/firebase-login", response_model=TokenResponse)
async def firebase_login(
    request: FirebaseLoginRequest, db: AsyncSession = Depends(get_db)
):
    """
    Verify Firebase ID token, create or fetch the user,
    and return a JWT access token.
    """
    try:
        firebase_user = await verify_firebase_token(request.id_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    uid = firebase_user["uid"]
    email = firebase_user["email"]

    # Check if user already exists
    result = await db.execute(select(User).where(User.firebase_uid == uid))
    user = result.scalar_one_or_none()

    if not user:
        # Create new user
        user = User(
            firebase_uid=uid,
            email=email,
            display_name=firebase_user.get("display_name"),
            profile_image=firebase_user.get("photo_url"),
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    # Generate JWT
    access_token = create_access_token({"sub": str(user.id), "email": user.email})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/complete-profile", response_model=UserResponse)
async def complete_profile(
    studio_name: str = Form(...),
    phone_number: str = Form(...),
    country_code: str = Form(...),
    profile_image: UploadFile = File(None),
    user_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Complete studio profile after initial Google auth."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.studio_name = studio_name
    user.phone_number = phone_number
    user.country_code = country_code
    user.profile_completed = True

    if profile_image:
        # Save profile image to local storage
        import os

        upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"profile_{user.id}_{profile_image.filename}")
        with open(file_path, "wb") as f:
            content = await profile_image.read()
            f.write(content)
        user.profile_image = f"/uploads/profile_{user.id}_{profile_image.filename}"

    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.put("/update-profile", response_model=UserResponse)
async def update_profile(
    user_id: int = Form(...),
    studio_name: str = Form(...),
    display_name: str = Form(...),
    phone_number: str = Form(...),
    country_code: str = Form(...),
    instagram_link: Optional[str] = Form(None),
    facebook_link: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    contact_numbers: Optional[str] = Form(None),
    website_link: Optional[str] = Form(None),
    whatsapp_number: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    profile_image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    """Update user's creative studio details."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.studio_name = studio_name
    user.display_name = display_name
    user.phone_number = phone_number
    user.country_code = country_code
    user.instagram_link = instagram_link
    user.facebook_link = facebook_link
    user.address = address
    user.contact_numbers = contact_numbers
    user.website_link = website_link
    user.whatsapp_number = whatsapp_number
    user.bio = bio

    if profile_image:
        # Save profile image to local storage
        import os

        upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"profile_{user.id}_{profile_image.filename}")
        with open(file_path, "wb") as f:
            content = await profile_image.read()
            f.write(content)
        user.profile_image = f"/uploads/profile_{user.id}_{profile_image.filename}"

    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def get_me(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get the current user's profile. (Uses query param for simplicity.)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.put("/tutorial-complete")
async def mark_tutorial_complete(user_id: int, db: AsyncSession = Depends(get_db)):
    """Mark the first-time tutorial as completed."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.first_login_tutorial = True
    await db.flush()
    return {"status": "ok"}

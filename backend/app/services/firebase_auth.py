"""Firebase authentication service — verifies ID tokens from the frontend."""

import httpx
from app.config import settings


async def verify_firebase_token(id_token: str) -> dict:
    """
    Verify a Firebase ID token using the Firebase REST API.
    Returns the decoded token payload with uid, email, etc.
    """
    url = (
        f"https://identitytoolkit.googleapis.com/v1/accounts:lookup"
        f"?key={settings.FIREBASE_API_KEY}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"idToken": id_token})

        if response.status_code != 200:
            raise ValueError(f"Firebase token verification failed: {response.text}")

        data = response.json()
        if "users" not in data or len(data["users"]) == 0:
            raise ValueError("No user found for this token")

        user_info = data["users"][0]
        return {
            "uid": user_info.get("localId"),
            "email": user_info.get("email"),
            "display_name": user_info.get("displayName"),
            "photo_url": user_info.get("photoUrl"),
            "email_verified": user_info.get("emailVerified", False),
        }

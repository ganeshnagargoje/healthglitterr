"""
Auth API Route

POST /api/auth/google-callback — exchanges Google auth code for user profile.
Keeps client_secret on the server side.
"""

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import config

router = APIRouter()


class GoogleCallbackRequest(BaseModel):
    code: str


@router.post("/google-callback")
async def google_callback(req: GoogleCallbackRequest):
    try:
        # Exchange code for tokens (server-side, secret stays here)
        async with httpx.AsyncClient() as client:
            token_res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": req.code,
                    "client_id": config.oauth.client_id,
                    "client_secret": config.oauth.client_secret,
                    "redirect_uri": config.oauth.redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
        token_data = token_res.json()

        if "access_token" not in token_data:
            raise HTTPException(status_code=401, detail="Token exchange failed")

        # Fetch user profile
        async with httpx.AsyncClient() as client:
            profile_res = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
        profile = profile_res.json()

        return {
            "name": profile.get("name", "User"),
            "email": profile.get("email", ""),
            "picture": profile.get("picture", ""),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

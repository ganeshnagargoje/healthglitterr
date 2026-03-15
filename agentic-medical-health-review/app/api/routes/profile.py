"""
Profile API Routes

POST /api/users/profile — save/update user profile (name, birth date, gender, height, weight).
GET  /api/users/profile?email=... — get user profile.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.infrastructure.repositories.postgres_user_repository import PostgresUserRepository

router = APIRouter()


class ProfileRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    birth_date: str  # YYYY-MM-DD
    gender: str
    height_cm: float
    weight_kg: float


@router.post("/profile")
async def save_profile(req: ProfileRequest):
    try:
        repo = PostgresUserRepository()
        user = repo.update_profile(
            email=req.email,
            first_name=req.first_name,
            last_name=req.last_name,
            birth_date=req.birth_date,
            gender=req.gender,
            height_cm=req.height_cm,
            weight_kg=req.weight_kg,
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "status": "ok",
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "birth_date": str(user.birth_date) if user.birth_date else None,
                "gender": user.gender,
                "height_cm": user.height_cm,
                "weight_kg": user.weight_kg,
                "profile_complete": user.profile_complete,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile")
async def get_profile(email: str):
    try:
        repo = PostgresUserRepository()
        user = repo.find_by_email(email)
        if not user:
            return {"profile_complete": False}
        return {
            "profile_complete": user.profile_complete,
            "first_name": user.first_name or '',
            "last_name": user.last_name or '',
            "birth_date": str(user.birth_date) if user.birth_date else '',
            "gender": user.gender or '',
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "role": user.role,
            "preferred_language": user.preferred_language,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
Consent API Routes

POST /api/users/consent — registers user consent with role and language.
GET  /api/users/consent-status?email=... — checks if user already consented.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.infrastructure.repositories.postgres_user_repository import PostgresUserRepository
from app.application.use_cases.register_consent import RegisterConsentUseCase

router = APIRouter()


class ConsentRequest(BaseModel):
    email: str
    name: str
    role: str
    language: str


@router.post("/consent")
async def register_consent(req: ConsentRequest):
    try:
        repo = PostgresUserRepository()
        use_case = RegisterConsentUseCase(user_repo=repo)
        user = use_case.execute(
            email=req.email,
            name=req.name,
            role=req.role,
            language=req.language,
        )
        return {
            "status": "ok",
            "user": {
                "email": user.email,
                "role": user.role,
                "preferred_language": user.preferred_language,
                "consent_status": user.consent_status,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consent-status")
async def consent_status(email: str):
    """Check if a user has already provided consent."""
    try:
        repo = PostgresUserRepository()
        user = repo.find_by_email(email)
        if user and user.consent_status:
            return {
                "consented": True,
                "role": user.role,
                "preferred_language": user.preferred_language,
            }
        return {"consented": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
User Domain Entity

Represents a user in the system with consent and profile management.
Framework-independent — no dependencies on outer layers.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class User:
    user_id: Optional[str] = None
    email: str = ''
    first_name: str = ''
    last_name: str = ''
    birth_date: Optional[date] = None
    gender: str = ''
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    role: str = 'patient'
    preferred_language: str = 'en'
    consent_status: bool = False
    consent_timestamp: Optional[datetime] = None
    profile_complete: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def grant_consent(self):
        self.consent_status = True
        self.consent_timestamp = datetime.utcnow()

    def revoke_consent(self):
        self.consent_status = False
        self.consent_timestamp = None

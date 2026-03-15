"""
User Domain Entity

Represents a user in the system with consent management.
Framework-independent — no dependencies on outer layers.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    user_id: Optional[str] = None
    email: str = ''
    name: str = ''
    role: str = 'patient'
    preferred_language: str = 'en'
    consent_status: bool = False
    consent_timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def grant_consent(self):
        self.consent_status = True
        self.consent_timestamp = datetime.utcnow()

    def revoke_consent(self):
        self.consent_status = False
        self.consent_timestamp = None

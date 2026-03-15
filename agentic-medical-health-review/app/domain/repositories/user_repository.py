"""
User Repository Interface (Port)

Defines the contract for user persistence.
Domain layer defines this — infrastructure implements it (DIP).
"""

from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def update_consent(self, email: str, role: str, language: str) -> Optional[User]:
        pass

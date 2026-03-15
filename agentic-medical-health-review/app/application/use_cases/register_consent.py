"""
Register Consent Use Case

Orchestrates user creation/update with consent information.
SRP: Handles only the consent registration workflow.
DIP: Depends on IUserRepository interface, not implementation.
"""

from app.domain.entities.user import User
from app.domain.repositories.user_repository import IUserRepository


class RegisterConsentUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def execute(self, email: str, name: str, role: str, language: str) -> User:
        existing = self.user_repo.find_by_email(email)

        if existing:
            updated = self.user_repo.update_consent(email, role, language)
            return updated

        user = User(email=email, name=name, role=role, preferred_language=language)
        user.grant_consent()
        return self.user_repo.save(user)

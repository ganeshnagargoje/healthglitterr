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
        # Split Google name into first/last
        parts = name.strip().split(' ', 1)
        first_name = parts[0] if parts else ''
        last_name = parts[1] if len(parts) > 1 else ''

        existing = self.user_repo.find_by_email(email)

        if existing:
            return self.user_repo.update_consent(email, role, language)

        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            preferred_language=language,
        )
        user.grant_consent()
        return self.user_repo.save(user)

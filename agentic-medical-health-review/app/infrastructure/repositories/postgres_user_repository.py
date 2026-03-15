"""
PostgreSQL User Repository Implementation (Adapter)

Implements IUserRepository using psycopg2.
LSP: Substitutable for the interface.
"""

from typing import Optional
from datetime import datetime
from app.domain.entities.user import User
from app.domain.repositories.user_repository import IUserRepository
from models.database_connection import DatabaseConnection


class PostgresUserRepository(IUserRepository):

    def find_by_email(self, email: str) -> Optional[User]:
        with DatabaseConnection() as db:
            db.cursor.execute(
                "SELECT * FROM users WHERE email = %s", (email,)
            )
            row = db.cursor.fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    def save(self, user: User) -> User:
        with DatabaseConnection() as db:
            db.cursor.execute(
                """INSERT INTO users (email, role, preferred_language, consent_status, consent_timestamp)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (email) DO UPDATE SET
                     role = EXCLUDED.role,
                     preferred_language = EXCLUDED.preferred_language,
                     consent_status = EXCLUDED.consent_status,
                     consent_timestamp = EXCLUDED.consent_timestamp
                   RETURNING *""",
                (user.email, user.role, user.preferred_language,
                 user.consent_status, user.consent_timestamp),
            )
            row = db.cursor.fetchone()
            return self._row_to_user(row)

    def update_consent(self, email: str, role: str, language: str) -> Optional[User]:
        now = datetime.utcnow()
        with DatabaseConnection() as db:
            db.cursor.execute(
                """UPDATE users
                   SET role = %s,
                       preferred_language = %s,
                       consent_status = TRUE,
                       consent_timestamp = %s
                   WHERE email = %s
                   RETURNING *""",
                (role, language, now, email),
            )
            row = db.cursor.fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    @staticmethod
    def _row_to_user(row: dict) -> User:
        return User(
            user_id=str(row['user_id']),
            email=row['email'],
            role=row['role'],
            preferred_language=row.get('preferred_language', 'en'),
            consent_status=row.get('consent_status', False),
            consent_timestamp=row.get('consent_timestamp'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
        )

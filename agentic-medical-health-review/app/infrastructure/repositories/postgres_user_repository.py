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
            db.cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = db.cursor.fetchone()
            if not row:
                return None
            return self._row_to_user(row)

    def save(self, user: User) -> User:
        with DatabaseConnection() as db:
            db.cursor.execute(
                """INSERT INTO users
                     (email, first_name, last_name, role, preferred_language,
                      consent_status, consent_timestamp)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (email) DO UPDATE SET
                     first_name = EXCLUDED.first_name,
                     last_name = EXCLUDED.last_name,
                     role = EXCLUDED.role,
                     preferred_language = EXCLUDED.preferred_language,
                     consent_status = EXCLUDED.consent_status,
                     consent_timestamp = EXCLUDED.consent_timestamp
                   RETURNING *""",
                (user.email, user.first_name, user.last_name,
                 user.role, user.preferred_language,
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

    def update_profile(self, email: str, first_name: str, last_name: str,
                       birth_date, gender: str, height_cm: float,
                       weight_kg: float) -> Optional[User]:
        with DatabaseConnection() as db:
            db.cursor.execute(
                """UPDATE users
                   SET first_name = %s,
                       last_name = %s,
                       birth_date = %s,
                       gender = %s,
                       height_cm = %s,
                       weight_kg = %s,
                       profile_complete = TRUE
                   WHERE email = %s
                   RETURNING *""",
                (first_name, last_name, birth_date, gender,
                 height_cm, weight_kg, email),
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
            first_name=row.get('first_name', ''),
            last_name=row.get('last_name', ''),
            birth_date=row.get('birth_date'),
            gender=row.get('gender', ''),
            height_cm=float(row['height_cm']) if row.get('height_cm') else None,
            weight_kg=float(row['weight_kg']) if row.get('weight_kg') else None,
            role=row['role'],
            preferred_language=row.get('preferred_language', 'en'),
            consent_status=row.get('consent_status', False),
            consent_timestamp=row.get('consent_timestamp'),
            profile_complete=row.get('profile_complete', False),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
        )

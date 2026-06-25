from datetime import datetime
from uuid import UUID

import asyncpg

from app.users.records import ActivationCodeRecord, UserRecord


def normalize_email(email: str) -> str:
    return email.strip().lower()


class UserRepository:
    def __init__(self, connection: asyncpg.Connection) -> None:
        self._connection = connection

    async def create_user(self, email: str, password_hash: str) -> UserRecord:
        normalized_email = normalize_email(email)

        record = await self._connection.fetchrow(
            """
            INSERT INTO users (email, password_hash)
            VALUES ($1, $2)
            RETURNING id, email, password_hash, is_active, created_at, activated_at
            """,
            normalized_email,
            password_hash,
        )

        return UserRecord.from_record(record)

    async def get_user_by_email(self, email: str) -> UserRecord | None:
        normalized_email = normalize_email(email)

        record = await self._connection.fetchrow(
            """
            SELECT id, email, password_hash, is_active, created_at, activated_at
            FROM users
            WHERE lower(email) = $1
            """,
            normalized_email,
        )

        if record is None:
            return None

        return UserRecord.from_record(record)

    async def activate_user(self, user_id: UUID) -> UserRecord:
        record = await self._connection.fetchrow(
            """
            UPDATE users
            SET is_active = TRUE,
                activated_at = now()
            WHERE id = $1
            RETURNING id, email, password_hash, is_active, created_at, activated_at
            """,
            user_id,
        )

        return UserRecord.from_record(record)

    async def invalidate_unused_activation_codes(self, user_id: UUID) -> None:
        await self._connection.execute(
            """
            UPDATE activation_codes
            SET used_at = now()
            WHERE user_id = $1
              AND used_at IS NULL
            """,
            user_id,
        )

    async def create_activation_code(
        self,
        user_id: UUID,
        code_hash: str,
        expires_at: datetime,
    ) -> ActivationCodeRecord:
        record = await self._connection.fetchrow(
            """
            INSERT INTO activation_codes (user_id, code_hash, expires_at)
            VALUES ($1, $2, $3)
            RETURNING id, user_id, code_hash, expires_at, used_at, attempts, created_at
            """,
            user_id,
            code_hash,
            expires_at,
        )

        return ActivationCodeRecord.from_record(record)

    async def get_latest_unused_activation_code(
        self,
        user_id: UUID,
    ) -> ActivationCodeRecord | None:
        record = await self._connection.fetchrow(
            """
            SELECT id, user_id, code_hash, expires_at, used_at, attempts, created_at
            FROM activation_codes
            WHERE user_id = $1
            AND used_at IS NULL
            ORDER BY created_at DESC
            LIMIT 1
            FOR UPDATE
            """,
            user_id,
        )

        if record is None:
            return None

        return ActivationCodeRecord.from_record(record)

    async def increment_activation_attempts(
        self,
        activation_code_id: UUID,
    ) -> ActivationCodeRecord:
        record = await self._connection.fetchrow(
            """
            UPDATE activation_codes
            SET attempts = attempts + 1
            WHERE id = $1
            RETURNING id, user_id, code_hash, expires_at, used_at, attempts, created_at
            """,
            activation_code_id,
        )

        return ActivationCodeRecord.from_record(record)

    async def mark_activation_code_used(
        self,
        activation_code_id: UUID,
    ) -> ActivationCodeRecord:
        record = await self._connection.fetchrow(
            """
            UPDATE activation_codes
            SET used_at = now()
            WHERE id = $1
            RETURNING id, user_id, code_hash, expires_at, used_at, attempts, created_at
            """,
            activation_code_id,
        )

        return ActivationCodeRecord.from_record(record)

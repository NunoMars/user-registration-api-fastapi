from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import asyncpg


@dataclass(frozen=True)
class UserRecord:
    id: UUID
    email: str
    password_hash: str
    is_active: bool
    created_at: datetime
    activated_at: datetime | None

    @classmethod
    def from_record(cls, record: asyncpg.Record) -> "UserRecord":
        return cls(
            id=record["id"],
            email=record["email"],
            password_hash=record["password_hash"],
            is_active=record["is_active"],
            created_at=record["created_at"],
            activated_at=record["activated_at"],
        )


@dataclass(frozen=True)
class ActivationCodeRecord:
    id: UUID
    user_id: UUID
    code_hash: str
    expires_at: datetime
    used_at: datetime | None
    attempts: int
    created_at: datetime

    @classmethod
    def from_record(cls, record: asyncpg.Record) -> "ActivationCodeRecord":
        return cls(
            id=record["id"],
            user_id=record["user_id"],
            code_hash=record["code_hash"],
            expires_at=record["expires_at"],
            used_at=record["used_at"],
            attempts=record["attempts"],
            created_at=record["created_at"],
        )

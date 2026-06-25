from datetime import datetime, timedelta, timezone

import asyncpg

from app.core.config import Settings
from app.core.exceptions import UserAlreadyExistsError
from app.core.security import (
    generate_activation_code,
    hash_activation_code,
    hash_password,
)
from app.email.client import EmailClient
from app.users.records import UserRecord
from app.users.repository import UserRepository

ACTIVATION_CODE_TTL_SECONDS = 60


class UserService:
    def __init__(
        self,
        pool: asyncpg.Pool,
        email_client: EmailClient,
        settings: Settings,
    ) -> None:
        self._pool = pool
        self._email_client = email_client
        self._settings = settings

    async def register_user(self, email: str, password: str) -> UserRecord:
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                repository = UserRepository(connection)

                existing_user = await repository.get_user_by_email(email)
                if existing_user is not None:
                    raise UserAlreadyExistsError()

                user = await repository.create_user(
                    email=email,
                    password_hash=hash_password(password),
                )

                activation_code = generate_activation_code()
                activation_code_hash = hash_activation_code(
                    code=activation_code,
                    user_id=user.id,
                    pepper=self._settings.activation_code_pepper,
                )

                expires_at = datetime.now(timezone.utc) + timedelta(
                    seconds=ACTIVATION_CODE_TTL_SECONDS,
                )

                await repository.create_activation_code(
                    user_id=user.id,
                    code_hash=activation_code_hash,
                    expires_at=expires_at,
                )

        await self._email_client.send_activation_code(
            email=user.email,
            code=activation_code,
        )

        return user

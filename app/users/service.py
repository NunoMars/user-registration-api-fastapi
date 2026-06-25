from datetime import datetime, timedelta, timezone

import asyncpg

from app.core.config import Settings
from app.core.exceptions import (
    ApiError,
    InvalidCredentialsError,
    InvalidOrExpiredActivationCodeError,
    TooManyActivationAttemptsError,
    UserAlreadyActiveError,
    UserAlreadyExistsError,
)
from app.core.security import (
    generate_activation_code,
    hash_activation_code,
    hash_password,
    verify_activation_code,
    verify_password,
)
from app.email.client import EmailClient
from app.users.records import UserRecord
from app.users.repository import UserRepository

ACTIVATION_CODE_TTL_SECONDS = 60
MAX_ACTIVATION_ATTEMPTS = 5


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

    async def activate_user(
        self,
        email: str,
        password: str,
        code: str,
    ) -> UserRecord:
        error_to_raise: ApiError | None = None

        async with self._pool.acquire() as connection:
            async with connection.transaction():
                repository = UserRepository(connection)

                user = await repository.get_user_by_email(email)
                if user is None:
                    raise InvalidCredentialsError()

                if not verify_password(password, user.password_hash):
                    raise InvalidCredentialsError()

                if user.is_active:
                    raise UserAlreadyActiveError()

                activation_code = await repository.get_latest_unused_activation_code(
                    user.id
                )
                if activation_code is None:
                    raise InvalidOrExpiredActivationCodeError()

                if activation_code.attempts >= MAX_ACTIVATION_ATTEMPTS:
                    raise TooManyActivationAttemptsError()

                now = datetime.now(timezone.utc)
                if activation_code.expires_at <= now:
                    raise InvalidOrExpiredActivationCodeError()

                is_code_valid = verify_activation_code(
                    plain_code=code,
                    code_hash=activation_code.code_hash,
                    user_id=user.id,
                    pepper=self._settings.activation_code_pepper,
                )

                if not is_code_valid:
                    updated_code = await repository.increment_activation_attempts(
                        activation_code.id,
                    )

                    if updated_code.attempts >= MAX_ACTIVATION_ATTEMPTS:
                        error_to_raise = TooManyActivationAttemptsError()
                    else:
                        error_to_raise = InvalidOrExpiredActivationCodeError()
                else:
                    await repository.mark_activation_code_used(activation_code.id)
                    return await repository.activate_user(user.id)

        if error_to_raise is not None:
            raise error_to_raise

        raise InvalidOrExpiredActivationCodeError()

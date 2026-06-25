import asyncio
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.db.pool import close_pool, create_pool
from app.db.schema_loader import apply_schema
from app.email.fake_client import get_email_client
from app.main import app


class InMemoryEmailClient:
    def __init__(self) -> None:
        self.activation_codes: dict[str, str] = {}

    async def send_activation_code(self, email: str, code: str) -> None:
        self.activation_codes[email] = code


async def reset_database() -> None:
    settings = get_settings()
    pool = await create_pool(settings.database_url)

    try:
        await apply_schema(pool)

        async with pool.acquire() as connection:
            await connection.execute("""
                TRUNCATE TABLE activation_codes, users
                RESTART IDENTITY CASCADE
                """)
    finally:
        await close_pool(pool)


async def execute_sql(query: str, *args: object) -> None:
    settings = get_settings()
    pool = await create_pool(settings.database_url)

    try:
        async with pool.acquire() as connection:
            await connection.execute(query, *args)
    finally:
        await close_pool(pool)


@pytest.fixture(autouse=True)
def clean_database() -> None:
    asyncio.run(reset_database())


@pytest.fixture
def email_client() -> InMemoryEmailClient:
    return InMemoryEmailClient()


@pytest.fixture
def client(email_client: InMemoryEmailClient) -> TestClient:
    app.dependency_overrides[get_email_client] = lambda: email_client

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def db_execute() -> Callable[..., None]:
    def execute(query: str, *args: object) -> None:
        asyncio.run(execute_sql(query, *args))

    return execute

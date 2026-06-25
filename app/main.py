from contextlib import asynccontextmanager

import asyncpg
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import ApiError
from app.db.pool import close_pool, create_pool, get_db_pool
from app.db.schema_loader import apply_schema
from app.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.db_pool = await create_pool(settings.database_url)

    if settings.apply_schema_on_startup:
        await apply_schema(app.state.db_pool)

    try:
        yield
    finally:
        await close_pool(app.state.db_pool)


app = FastAPI(
    title="User Registration API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(ApiError)
async def api_error_handler(
    request: Request,
    exc: ApiError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


app.include_router(users_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
async def readiness_check(
    pool: asyncpg.Pool = Depends(get_db_pool),
) -> dict[str, str]:
    async with pool.acquire() as connection:
        await connection.fetchval("SELECT 1")

    return {"status": "ready"}

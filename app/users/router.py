import asyncpg
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.config import Settings, get_settings
from app.db.pool import get_db_pool
from app.email.client import EmailClient
from app.email.fake_client import get_email_client
from app.users.schemas import ActivateUserRequest, RegisterUserRequest, UserResponse
from app.users.service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])
basic_auth = HTTPBasic()


def get_user_service(
    pool: asyncpg.Pool = Depends(get_db_pool),
    email_client: EmailClient = Depends(get_email_client),
    settings: Settings = Depends(get_settings),
) -> UserService:
    return UserService(
        pool=pool,
        email_client=email_client,
        settings=settings,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
async def register_user(
    payload: RegisterUserRequest,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await user_service.register_user(
        email=str(payload.email),
        password=payload.password,
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
    )


@router.post(
    "/activate",
    response_model=UserResponse,
)
async def activate_user(
    payload: ActivateUserRequest,
    credentials: HTTPBasicCredentials = Depends(basic_auth),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await user_service.activate_user(
        email=credentials.username,
        password=credentials.password,
        code=payload.code,
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
    )

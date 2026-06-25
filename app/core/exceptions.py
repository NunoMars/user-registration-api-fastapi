from dataclasses import dataclass


@dataclass(frozen=True)
class ApiError(Exception):
    code: str
    message: str
    status_code: int


class UserAlreadyExistsError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            code="USER_ALREADY_EXISTS",
            message="A user with this email already exists.",
            status_code=409,
        )


class InvalidPasswordError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            code="INVALID_PASSWORD",
            message="Password does not meet security requirements.",
            status_code=400,
        )

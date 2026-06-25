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


class InvalidCredentialsError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            code="INVALID_CREDENTIALS",
            message="Invalid credentials.",
            status_code=401,
        )


class UserAlreadyActiveError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            code="USER_ALREADY_ACTIVE",
            message="User account is already active.",
            status_code=409,
        )


class InvalidOrExpiredActivationCodeError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            code="INVALID_OR_EXPIRED_ACTIVATION_CODE",
            message="Activation code is invalid or expired.",
            status_code=400,
        )


class TooManyActivationAttemptsError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            code="TOO_MANY_ACTIVATION_ATTEMPTS",
            message="Too many activation attempts.",
            status_code=429,
        )

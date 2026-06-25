import hashlib
import hmac
import secrets
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError

_password_hasher = PasswordHasher()


class InvalidActivationCodeFormat(ValueError):
    pass


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, plain_password)
    except (VerifyMismatchError, VerificationError):
        return False


def generate_activation_code() -> str:
    return f"{secrets.randbelow(10_000):04d}"


def validate_activation_code_format(code: str) -> None:
    if len(code) != 4 or not code.isdigit():
        raise InvalidActivationCodeFormat(
            "Activation code must contain exactly 4 digits"
        )


def hash_activation_code(code: str, user_id: UUID, pepper: str) -> str:
    validate_activation_code_format(code)

    payload = f"{user_id}:{code}".encode("utf-8")
    secret = pepper.encode("utf-8")

    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def verify_activation_code(
    plain_code: str,
    code_hash: str,
    user_id: UUID,
    pepper: str,
) -> bool:
    try:
        candidate_hash = hash_activation_code(plain_code, user_id, pepper)
    except InvalidActivationCodeFormat:
        return False

    return hmac.compare_digest(candidate_hash, code_hash)

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        has_letter = any(char.isalpha() for char in value)
        has_digit = any(char.isdigit() for char in value)

        if not has_letter or not has_digit:
            raise ValueError("Password must contain at least one letter and one digit")

        return value


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

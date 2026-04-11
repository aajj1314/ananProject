"""Authentication schemas."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    """Login request body."""

    phone: str = Field(min_length=11, max_length=11)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Ensure phone number format."""

        if not value.isdigit():
            raise ValueError("Phone must contain exactly 11 digits")
        return value


class RegisterRequest(LoginRequest):
    """Registration request body."""

    nickname: str = Field(min_length=1, max_length=50)


class TokenPayload(BaseModel):
    """JWT token response body."""

    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    """User profile response."""

    id: int
    phone: str
    nickname: str
    role: str
    created_at: datetime


class UserUpdate(BaseModel):
    """Update user profile request body."""

    nickname: str | None = Field(default=None, min_length=1, max_length=50)


class PasswordReset(BaseModel):
    """Reset password request body."""

    old_password: str = Field(min_length=6, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)

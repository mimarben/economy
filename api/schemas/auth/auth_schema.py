from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

from schemas.users.user_schema import check_password


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """Schema for user registration — maps to UserCreate fields."""
    name: str = Field(..., min_length=1, max_length=255)
    surname1: str = Field(..., min_length=1, max_length=255)
    surname2: Optional[str] = None
    dni: str
    email: EmailStr
    telephone: Optional[int] = None
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class RefreshResponse(BaseModel):
    """Schema for refresh token response."""
    access_token: str
    token_type: str = "Bearer"


class ChangePasswordRequest(BaseModel):
    """Schema for changing own password (requires the current one)."""
    current_password: str = Field(..., min_length=1)
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return check_password(value)

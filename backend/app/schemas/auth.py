"""Pydantic schemas for authentication endpoints."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Credentials for user login."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RegisterRequest(BaseModel):
    """New user registration payload."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=255)


class UserResponse(BaseModel):
    """Public-facing user representation (no password hash)."""

    id: str
    email: EmailStr
    full_name: Optional[str]
    role: str
    is_active: bool

    model_config = {"from_attributes": True}

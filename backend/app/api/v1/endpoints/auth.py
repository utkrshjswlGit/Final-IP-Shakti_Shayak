"""Authentication endpoints — login and registration."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.security import create_access_token, hash_password, verify_password
from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=201, tags=["Auth"])
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Register a new user account."""
    existing = await db.execute(
        select(User).where(User.email == payload.email.lower())
    )
    if existing.scalar_one_or_none() is not None:
        raise ValidationError(message="An account with this email already exists.")

    user = User(
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse, tags=["Auth"])
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate a user and return a JWT access token."""
    result = await db.execute(
        select(User).where(User.email == payload.email.lower())
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise AuthenticationError(message="Invalid email or password.")

    if not user.is_active:
        raise AuthenticationError(message="Account is inactive.")

    token = create_access_token(subject=str(user.id))

    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse, tags=["Auth"])
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)

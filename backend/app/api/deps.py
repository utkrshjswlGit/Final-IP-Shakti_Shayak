"""FastAPI dependency functions (reusable across endpoints)."""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole

_http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_http_bearer),
) -> User:
    """Dependency: validates Bearer JWT and returns the current user."""
    if credentials is None:
        raise AuthenticationError(message="Authentication credentials not provided.")

    payload = decode_access_token(credentials.credentials)
    user_id: str = payload.get("sub", "")

    if not user_id:
        raise AuthenticationError(message="Token subject is missing.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise AuthenticationError(message="User not found or inactive.")

    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency: requires the authenticated user to be an admin."""
    if current_user.role != UserRole.ADMIN:
        raise AuthorizationError(message="Admin privileges required.")
    return current_user

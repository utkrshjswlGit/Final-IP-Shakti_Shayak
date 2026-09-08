"""User ORM model."""

from __future__ import annotations

import enum
from typing import List, Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Registered application user."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(254), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # Stored as string for SQLite/PostgreSQL compatibility
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default=UserRole.USER.value
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    sessions: Mapped[List["WorkspaceSession"]] = relationship(  # noqa: F821
        "WorkspaceSession", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(  # noqa: F821
        "AuditLog", back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"

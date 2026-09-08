"""SQLAlchemy declarative base and shared column helpers.

Uses dialect-agnostic types where possible so the same models work
with both SQLite (tests) and PostgreSQL (production).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


class TimestampMixin:
    """Mixin providing created_at / updated_at timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(tz=timezone.utc),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """Mixin providing a UUID primary key (stored as String for cross-DB compatibility)."""

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

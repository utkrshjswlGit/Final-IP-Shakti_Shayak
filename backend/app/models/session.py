"""Session ORM model."""

from __future__ import annotations

import enum
from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Jurisdiction(str, enum.Enum):
    INDIA = "india"
    INTERNATIONAL = "international"


class WorkspaceSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A user's assessment workspace session."""

    __tablename__ = "sessions"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    current_jurisdiction: Mapped[str] = mapped_column(
        String(20), nullable=False, default=Jurisdiction.INDIA.value
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")  # noqa: F821
    assessments: Mapped[List["Assessment"]] = relationship(  # noqa: F821
        "Assessment", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<WorkspaceSession id={self.id} user_id={self.user_id}>"

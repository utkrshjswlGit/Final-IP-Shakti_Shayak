"""AuditLog ORM model — immutable audit trail."""

from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin


class AuditLog(Base, UUIDPrimaryKeyMixin):
    """Immutable audit trail. Write-once at the application layer."""

    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    target_resource: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    metadata_: Mapped[Optional[Dict]] = mapped_column("metadata", JSON, nullable=True)
    timestamp: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action}>"

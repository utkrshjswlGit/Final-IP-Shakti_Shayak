"""Assessment ORM model."""

from __future__ import annotations

import enum
from typing import Any, Dict, List, Optional

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AssessmentStatus(str, enum.Enum):
    INTAKE = "intake"
    CLARIFYING = "clarifying"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    ESCALATED = "escalated"
    FAILED = "failed"


class Assessment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """An innovation assessment record."""

    __tablename__ = "assessments"

    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    innovation_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=AssessmentStatus.INTAKE.value
    )

    # Structured analysis outputs — null until analysis completes
    classification_data: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    ip_assessment: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    tk_assessment: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    abs_assessment: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    action_plan: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    clarification_history: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
    escalation_brief: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    session: Mapped["WorkspaceSession"] = relationship(  # noqa: F821
        "WorkspaceSession", back_populates="assessments"
    )

    def __repr__(self) -> str:
        return f"<Assessment id={self.id} status={self.status}>"

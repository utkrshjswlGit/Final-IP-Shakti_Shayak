"""Models package — imports all ORM models to ensure SQLAlchemy mapper
resolves all forward references correctly regardless of import order."""

from __future__ import annotations

from app.models.user import User, UserRole  # noqa: F401
from app.models.session import WorkspaceSession, Jurisdiction  # noqa: F401
from app.models.assessment import Assessment, AssessmentStatus  # noqa: F401
from app.models.document import Document, DocumentChunk, TrustTier, DocumentStatus, DocumentJurisdiction  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401

__all__ = [
    "User",
    "UserRole",
    "WorkspaceSession",
    "Jurisdiction",
    "Assessment",
    "AssessmentStatus",
    "Document",
    "DocumentChunk",
    "TrustTier",
    "DocumentStatus",
    "DocumentJurisdiction",
    "AuditLog",
]

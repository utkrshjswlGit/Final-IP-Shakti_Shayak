"""Document and DocumentChunk ORM models — the knowledge base."""

from __future__ import annotations

import enum
from typing import List, Optional

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# pgvector for production; plain JSON fallback for tests
try:
    from pgvector.sqlalchemy import Vector as _Vector

    def _vector_column(dim: int) -> Column:  # type: ignore[type-arg]
        return Column(_Vector(dim), nullable=True)

except ImportError:
    from sqlalchemy import JSON
    def _vector_column(dim: int) -> Column:  # type: ignore[type-arg]
        return Column(JSON, nullable=True)


class TrustTier(int, enum.Enum):
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class DocumentStatus(str, enum.Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    DRAFT = "draft"


class DocumentJurisdiction(str, enum.Enum):
    INDIA = "india"
    INTERNATIONAL = "international"


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Metadata record for an ingested authoritative document."""

    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    authority: Mapped[str] = mapped_column(String(500), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    publication_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    effective_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=DocumentStatus.ACTIVE.value
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, unique=True)
    trust_tier: Mapped[int] = mapped_column(Integer, nullable=False, default=TrustTier.TIER_2)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")

    chunks: Mapped[List["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} title={self.title[:50]}>"


class DocumentChunk(Base, UUIDPrimaryKeyMixin):
    """A semantic chunk of a document with its embedding vector."""

    __tablename__ = "document_chunks"

    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    hierarchy_level_1: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    hierarchy_level_2: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    hierarchy_level_3: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    page_num: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    char_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    char_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # pgvector in production, Text fallback in tests
    embedding = _vector_column(1536)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk id={self.id} document_id={self.document_id}>"

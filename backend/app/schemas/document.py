"""Pydantic schemas for document / knowledge base endpoints."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TrustTierEnum(int, Enum):
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class DocumentJurisdictionEnum(str, Enum):
    INDIA = "india"
    INTERNATIONAL = "international"


class DocumentStatusEnum(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    DRAFT = "draft"


class DocumentMetadataResponse(BaseModel):
    """Public metadata for a knowledge-base document."""

    id: str
    title: str
    authority: str
    jurisdiction: DocumentJurisdictionEnum
    domain: str
    document_type: str
    version: Optional[str]
    publication_date: Optional[str]
    effective_date: Optional[str]
    status: DocumentStatusEnum
    source_url: Optional[str]
    trust_tier: TrustTierEnum
    language: str

    model_config = {"from_attributes": True}

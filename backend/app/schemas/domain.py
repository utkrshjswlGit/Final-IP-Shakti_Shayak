"""Schemas for domain-specific assessments (Phase 4)."""

import enum
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from app.schemas.rag import Claim, EvidenceStrength

class DomainState(str, enum.Enum):
    SUPPORTED = "SUPPORTED"
    POTENTIALLY_RELEVANT = "POTENTIALLY_RELEVANT"
    REVIEW = "REVIEW"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOT_IDENTIFIED = "NOT_IDENTIFIED"

class DomainResult(BaseModel):
    """Standardized output format for every domain assessment."""
    domain_name: str = Field(description="Name of the assessment domain (e.g., 'ABS_SCREENING').")
    status: DomainState = Field(description="Overall evaluation status.")
    reasoning: str = Field(description="Detailed explanation avoiding explicit legal yes/no conclusions.")
    evidence: List[Claim] = Field(description="List of verified claims and citations.")
    confidence: EvidenceStrength = Field(description="The strength of the underlying evidence.")
    missing_information: List[str] = Field(description="List of data points missing to complete the assessment.")
    next_step: str = Field(description="Actionable next step for the user.")

class ProductClassification(BaseModel):
    """Output of the product classification engine."""
    product_type: str = Field(description="e.g., botanical, formulation, process, device")
    key_ingredients: List[str] = Field(description="Identified ingredients, herbs, or components.")
    is_traditional_medicine: bool = Field(description="Whether the product falls under traditional medicine frameworks.")
    has_foreign_involvement: bool = Field(description="Whether the user or target market triggers international/foreign entity rules.")

class UserContext(BaseModel):
    """Context provided by the user for the assessment."""
    description: str
    citizenship: str = "india"
    entity_type: str = "individual" # individual, company, research_institution
    target_markets: List[str] = ["india"]

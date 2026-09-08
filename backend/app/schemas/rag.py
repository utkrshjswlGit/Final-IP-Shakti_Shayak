"""Pydantic schemas for the RAG generation layer."""

from __future__ import annotations

import enum
from typing import List, Optional, Dict

from pydantic import BaseModel, Field

class IntentCategory(str, enum.Enum):
    PATENT_ELIGIBILITY = "patent_eligibility"
    BIODIVERSITY_ABS = "biodiversity_abs"
    TRADITIONAL_KNOWLEDGE = "traditional_knowledge"
    GENERAL_INQUIRY = "general_inquiry"
    UNCLEAR = "unclear"

class EvidenceStrength(str, enum.Enum):
    STRONG = "strong"         # Verified claims backed by Tier 1 sources
    MODERATE = "moderate"     # Verified claims backed by Tier 2/3 sources
    WEAK = "weak"             # Unverified citations or conflicting sources
    INSUFFICIENT = "insufficient" # No evidence, safe abstention triggered

class AbstentionReason(str, enum.Enum):
    NO_EVIDENCE = "no_relevant_evidence"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    WRONG_JURISDICTION = "wrong_jurisdiction"
    OUTDATED_SOURCE = "outdated_source"
    MISSING_INFO = "missing_user_information"
    NONE = "none"

class Claim(BaseModel):
    """A single substantive legal/regulatory claim made by the LLM."""
    text: str = Field(description="The substantive claim text.")
    citations: List[str] = Field(description="List of chunk IDs supporting this claim.")
    verified: bool = Field(default=False, description="Whether the citations were verified post-generation.")

class LLMStructuredOutput(BaseModel):
    """The raw structured output from the LLM."""
    intent: IntentCategory = Field(description="The classified intent of the user's query.")
    abstention_reason: AbstentionReason = Field(description="Reason for abstention if applicable, else NONE.")
    clarifying_question: Optional[str] = Field(default=None, description="A question to ask the user if information is missing.")
    claims: List[Claim] = Field(description="List of factual claims with citations.")
    summary: str = Field(description="A brief summary of the assessment.")

class GroundedAssessment(BaseModel):
    """The final verified output returned to the client."""
    query: str
    jurisdiction: str
    intent: IntentCategory
    strength: EvidenceStrength
    abstention_reason: AbstentionReason
    clarifying_question: Optional[str]
    claims: List[Claim]
    summary: str
    sources_used: List[Dict[str, str]] = Field(description="Metadata of the documents used.")

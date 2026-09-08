"""Pydantic schemas for assessment and session endpoints."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JurisdictionEnum(str, Enum):
    INDIA = "india"
    INTERNATIONAL = "international"


class AssessmentStatusEnum(str, Enum):
    INTAKE = "intake"
    CLARIFYING = "clarifying"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    ESCALATED = "escalated"
    FAILED = "failed"


class SessionCreateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    jurisdiction: JurisdictionEnum = JurisdictionEnum.INDIA


class SessionResponse(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    current_jurisdiction: JurisdictionEnum

    model_config = {"from_attributes": True}


class AssessmentInitRequest(BaseModel):
    """Payload to start a new assessment within a session."""

    innovation_description: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        description="Description of the Ayurveda innovation, product, or process.",
    )


class ClarificationAnswerItem(BaseModel):
    question_id: str
    answer: str = Field(..., max_length=2000)


class ClarificationRequest(BaseModel):
    answers: List[ClarificationAnswerItem]


class AssessmentResponse(BaseModel):
    """Full assessment record returned to the frontend."""

    id: str
    session_id: str
    status: AssessmentStatusEnum
    innovation_description: str

    classification_data: Optional[Dict[str, Any]] = None
    ip_assessment: Optional[Dict[str, Any]] = None
    tk_assessment: Optional[Dict[str, Any]] = None
    abs_assessment: Optional[Dict[str, Any]] = None
    action_plan: Optional[Dict[str, Any]] = None
    escalation_brief: Optional[Dict[str, Any]] = None
    clarification_history: Optional[List[Any]] = None

    model_config = {"from_attributes": True}

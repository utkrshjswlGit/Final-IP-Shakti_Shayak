"""Session and Assessment endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.assessment import Assessment, AssessmentStatus
from app.models.session import Jurisdiction, WorkspaceSession
from app.models.user import User
from app.schemas.assessment import (
    AssessmentInitRequest,
    AssessmentResponse,
    SessionCreateRequest,
    SessionResponse,
)

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse, status_code=201, tags=["Sessions"])
async def create_session(
    payload: SessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionResponse:
    """Create a new assessment workspace session."""
    session = WorkspaceSession(
        user_id=current_user.id,
        title=payload.title,
        current_jurisdiction=Jurisdiction(payload.jurisdiction.value),
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return SessionResponse.model_validate(session)


@router.get("/sessions", response_model=List[SessionResponse], tags=["Sessions"])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[SessionResponse]:
    """List all workspace sessions for the current user."""
    result = await db.execute(
        select(WorkspaceSession)
        .where(WorkspaceSession.user_id == current_user.id)
        .order_by(WorkspaceSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return [SessionResponse.model_validate(s) for s in sessions]


@router.get("/sessions/{session_id}", response_model=SessionResponse, tags=["Sessions"])
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionResponse:
    """Retrieve a specific session by ID."""
    result = await db.execute(
        select(WorkspaceSession).where(
            WorkspaceSession.id == session_id,
            WorkspaceSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise NotFoundError(message="Session not found.")
    return SessionResponse.model_validate(session)


@router.post(
    "/sessions/{session_id}/assessments",
    response_model=AssessmentResponse,
    status_code=201,
    tags=["Assessments"],
)
async def init_assessment(
    session_id: str,
    payload: AssessmentInitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentResponse:
    """Start a new assessment for a given session (Phase 1 stub)."""
    result = await db.execute(
        select(WorkspaceSession).where(
            WorkspaceSession.id == session_id,
            WorkspaceSession.user_id == current_user.id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise NotFoundError(message="Session not found.")

    assessment = Assessment(
        session_id=session_id,
        innovation_description=payload.innovation_description,
        status=AssessmentStatus.INTAKE,
    )
    db.add(assessment)
    await db.flush()
    await db.refresh(assessment)
    return AssessmentResponse.model_validate(assessment)


@router.get(
    "/sessions/{session_id}/assessments/{assessment_id}",
    response_model=AssessmentResponse,
    tags=["Assessments"],
)
async def get_assessment(
    session_id: str,
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentResponse:
    """Retrieve an assessment by ID."""
    result = await db.execute(
        select(Assessment)
        .join(WorkspaceSession)
        .where(
            Assessment.id == assessment_id,
            Assessment.session_id == session_id,
            WorkspaceSession.user_id == current_user.id,
        )
    )
    assessment = result.scalar_one_or_none()
    if assessment is None:
        raise NotFoundError(message="Assessment not found.")
    return AssessmentResponse.model_validate(assessment)

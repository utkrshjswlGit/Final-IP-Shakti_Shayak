"""Health check endpoint."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db

router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str
    timestamp: str
    database: str


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Return application health status including database connectivity."""
    db_status = "unreachable"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        timestamp=datetime.now(tz=timezone.utc).isoformat(),
        database=db_status,
    )

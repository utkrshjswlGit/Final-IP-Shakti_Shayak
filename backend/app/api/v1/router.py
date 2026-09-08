"""API v1 router — aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, sessions

router = APIRouter()

router.include_router(health.router)
router.include_router(auth.router, prefix="/auth")
router.include_router(sessions.router)

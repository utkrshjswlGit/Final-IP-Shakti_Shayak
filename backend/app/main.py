"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import router as v1_router
import app.models  # noqa: F401 — ensures all ORM models are registered before mapper config
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — startup and shutdown logic."""
    configure_logging()
    logger = get_logger(__name__)
    logger.info(
        "startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )
    yield
    logger.info("shutdown", app_name=settings.app_name)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "IP-SAKTI Sahayak — Multilingual RAG-based AI assistant for Ayurveda IP "
            "and regulatory guidance. Decision-support only, not legal advice."
        ),
        docs_url="/docs" if settings.app_env != "production" else None,
        redoc_url="/redoc" if settings.app_env != "production" else None,
        lifespan=lifespan,
    )

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------
    # Exception Handlers
    # ------------------------------------------------------------------
    register_exception_handlers(app)

    # ------------------------------------------------------------------
    # Routers
    # ------------------------------------------------------------------
    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()

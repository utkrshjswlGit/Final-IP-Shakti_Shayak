"""Application configuration — loaded from environment variables.

Uses pydantic-settings so all values are type-validated on startup.
Fails immediately if required variables are missing.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings.

    All values are read from environment variables (case-insensitive).
    Falls back to .env file if present.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    app_name: str = "IP-SAKTI Sahayak"
    app_version: str = "0.1.0"
    app_env: Literal["development", "production", "test"] = "development"

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------
    secret_key: str = Field(..., min_length=32, description="JWT signing key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    database_url: str = Field(
        ..., description="Async SQLAlchemy DSN (asyncpg)"
    )
    database_url_sync: str = Field(
        ..., description="Sync SQLAlchemy DSN for Alembic (psycopg2)"
    )

    # ------------------------------------------------------------------
    # AI / LLM
    # ------------------------------------------------------------------
    llm_provider: Literal["mock", "openai", "azure_openai"] = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_reload: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    cors_origins: str = "http://localhost:3000"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str) -> str:
        """Accept comma-separated origins string."""
        return v

    def get_cors_origins_list(self) -> list[str]:
        """Return parsed list of allowed CORS origins."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # ------------------------------------------------------------------
    # Rate Limiting
    # ------------------------------------------------------------------
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()  # type: ignore[call-arg]

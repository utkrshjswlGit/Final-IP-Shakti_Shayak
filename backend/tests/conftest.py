"""Shared test fixtures and configuration.

IMPORTANT: Environment variables MUST be set before importing any app modules,
because pydantic-settings reads them at import time via the Settings singleton.
"""

from __future__ import annotations

import os

# Set test environment FIRST — before any app imports
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test_secret_key_minimum_32_characters_long_for_testing"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["DATABASE_URL_SYNC"] = "sqlite:///./test.db"
os.environ["LLM_PROVIDER"] = "mock"

# Now clear the settings cache so any cached settings from prior imports are invalidated
from app.core.config import get_settings  # noqa: E402
get_settings.cache_clear()

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from collections.abc import AsyncGenerator  # noqa: E402

from httpx import AsyncClient, ASGITransport  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

from app.db.base import Base  # noqa: E402
# Import ALL models so SQLAlchemy can resolve forward-reference relationships
import app.models.user  # noqa: F401, E402
import app.models.session  # noqa: F401, E402
import app.models.assessment  # noqa: F401, E402
import app.models.document  # noqa: F401, E402
import app.models.audit  # noqa: F401, E402
from app.main import app  # noqa: E402
from app.db.session import get_db  # noqa: E402

# Rebuild the test engine using the now-correct test DB URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create all tables once for the test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session, rolling back after each test."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTPX async test client wired to the test DB."""

    async def override_get_db():
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

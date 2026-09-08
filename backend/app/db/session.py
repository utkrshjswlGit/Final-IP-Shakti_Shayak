"""SQLAlchemy async database session factory.

The engine is created lazily on first use to allow tests to override
the DATABASE_URL environment variable before the module is imported.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


def _create_engine():
    """Create the async engine with settings appropriate for the DB dialect."""
    settings = get_settings()
    url = settings.database_url

    # SQLite (used in tests) does not support connection pool options.
    is_sqlite = url.startswith("sqlite")

    kwargs = {
        "echo": settings.app_env == "development",
        "pool_pre_ping": not is_sqlite,
    }
    if not is_sqlite:
        kwargs["pool_size"] = 10
        kwargs["max_overflow"] = 20

    if is_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False}

    return create_async_engine(url, **kwargs)


# Create engine at module import time but using the lazy factory
# so tests can set env vars before conftest imports this module.
engine = _create_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

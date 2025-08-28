"""Database engine and session setup for SQLAlchemy (async).

This module configures the async database engine and provides
a session factory (`AsyncSessionLocal`) for dependency injection.
"""


from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def _make_engine() -> AsyncEngine:
    """Create the global async database engine.

    Uses connection settings from `app.core.config.settings` and
    enables `pool_pre_ping` to validate connections.

    Returns:
        AsyncEngine: Configured SQLAlchemy async engine.
    """
    return create_async_engine(
        settings.get_async_database_url(),
        future=True,
        pool_pre_ping=True,
    )


engine = _make_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

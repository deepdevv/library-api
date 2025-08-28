import asyncio
import os

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from collections.abc import AsyncGenerator
from app.api.deps import get_session
from httpx import AsyncClient, ASGITransport
from app.main import app

# --- pytest-asyncio ----------------------------------------------------------

# Force pytest-asyncio to use asyncio mode
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def event_loop():
    """Use a session-scoped event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# --- Database setup/teardown -------------------------------------------------

@pytest_asyncio.fixture
async def prepare_database() -> AsyncGenerator[None, None]:
    # ensure no pooled connections from a different loop
    await engine.dispose()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # optional: dispose again to avoid cross-loop reuse
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(prepare_database) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            try:
                await session.rollback()
            except Exception:
                pass


@pytest_asyncio.fixture
async def client(db_session):
    async def _override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session

    # Build a transport that works across httpx versions
    try:
        # httpx versions that support the 'lifespan' kwarg
        transport = ASGITransport(app=app, lifespan="on")  # type: ignore[arg-type]
    except TypeError:
        # Older/newer variants without the kwarg
        transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

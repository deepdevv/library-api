"""Dependency providers for FastAPI routes.

These functions wire application services and database sessions
into request handlers via FastAPI's dependency injection system.
"""


from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.services.books import BookService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a SQLAlchemy `AsyncSession` for a single request.

    Yields:
        AsyncSession: Database session bound to the current request context.

    Ensures:
        - Connection is properly closed after use.
        - Safe usage in async environments with `async with`.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def get_book_service(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[BookService, None]:
    """Provide a `BookService` bound to a request-scoped session.

    Args:
        session (AsyncSession): Injected async session from `get_session`.

    Yields:
        BookService: Service instance for handling book business logic.
    """
    yield BookService(session)

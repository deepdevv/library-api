from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.services.books import BookService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a SQLAlchemy AsyncSession, ensuring proper cleanup."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_book_service(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[BookService, None]:
    """Dependency-injected BookService bound to a DB session."""
    yield BookService(session)

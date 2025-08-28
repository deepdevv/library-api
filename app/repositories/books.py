"""Repository layer for book persistence.

This module provides low-level data-access operations for the `Book` model.
No business logic is applied here; that is handled in the service layer.
"""


from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional, Tuple

from sqlalchemy import func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.models.book import Book
from sqlalchemy import and_, func, select


class BookRepository:
    """Data-access layer for `Book` objects."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with a database session."""
        self.session = session

    # --- helpers -------------------------------------------------------------

    def _base_query(
        self,
        *,
        is_borrowed: Optional[bool] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
    ) -> Select:
        """Build a SELECT statement with optional filters.

        Args:
            is_borrowed (Optional[bool]): Filter by borrow status.
            title (Optional[str]): Case-insensitive substring filter on title.
            author (Optional[str]): Case-insensitive substring filter on author.

        Returns:
            Select: SQLAlchemy SELECT statement.
        """
        stmt = select(Book)

        if is_borrowed is not None:
            stmt = stmt.where(Book.is_borrowed == is_borrowed)

        if title:
            stmt = stmt.where(Book.title.ilike(f"%{title.strip()}%"))

        if author:
            stmt = stmt.where(Book.author.ilike(f"%{author.strip()}%"))

        # Stable ordering for pagination
        stmt = stmt.order_by(Book.created_at.desc(), Book.serial_number.asc())
        return stmt

    # --- CRUD ---------------------------------------------------------------

    async def create(self, *, serial_number: str, title: str, author: str) -> Book:
        """Insert a new book row into the database."""
        obj = Book(
            serial_number=serial_number,
            title=title,
            author=author,
            is_borrowed=False,
            borrower_card=None,
            borrowed_at=None,
        )
        self.session.add(obj)
        await self.session.flush()  # get defaults like created_at/updated_at
        return obj

    async def get_by_serial(self, serial_number: str) -> Optional[Book]:
        """Retrieve a book by its serial number."""
        res = await self.session.execute(
            select(Book).where(Book.serial_number == serial_number)
        )
        return res.scalar_one_or_none()

    async def get_for_update(self, serial_number: str) -> Optional[Book]:
        """Fetch a book row with a FOR UPDATE lock (for state transitions)."""
        res = await self.session.execute(
            select(Book)
            .where(Book.serial_number == serial_number)
            .with_for_update()
        )
        return res.scalar_one_or_none()

    async def delete(self, serial_number: str) -> None:
        """Delete a book by its serial number."""
        await self.session.execute(
            delete(Book).where(Book.serial_number == serial_number)
        )
    
    async def list(
        self,
        *,
        is_borrowed: Optional[bool] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[Iterable[Book], int]:
        """Return a page of books with optional filters and total count.

        Args:
            is_borrowed (Optional[bool]): Filter by borrow status.
            title (Optional[str]): Case-insensitive substring filter on title.
            author (Optional[str]): Case-insensitive substring filter on author.
            limit (int): Maximum number of rows to return.
            offset (int): Offset for pagination.

        Returns:
            tuple[list[Book], int]: Books matching the filters and total count.
        """
        # filters reused for both queries
        conditions = []
        if is_borrowed is not None:
            conditions.append(Book.is_borrowed == is_borrowed)
        if title:
            conditions.append(Book.title.ilike(f"%{title.strip()}%"))
        if author:
            conditions.append(Book.author.ilike(f"%{author.strip()}%"))

        where_clause = and_(*conditions) if conditions else None

        # total
        count_stmt = select(func.count()).select_from(Book)
        if where_clause is not None:
            count_stmt = count_stmt.where(where_clause)
        total = (await self.session.execute(count_stmt)).scalar_one()

        # page
        page_stmt = select(Book)
        if where_clause is not None:
            page_stmt = page_stmt.where(where_clause)
        page_stmt = page_stmt.order_by(Book.created_at.desc(), Book.serial_number.asc())
        page_stmt = page_stmt.limit(limit).offset(offset)

        result = await self.session.execute(page_stmt)
        items = result.scalars().all()
        return items, int(total)

    async def update_borrow_state(
        self,
        *,
        serial_number: str,
        is_borrowed: bool,
        borrower_card: Optional[str],
        borrowed_at: Optional[datetime],
    ) -> Optional[Book]:
        """Update borrow-related fields of a book (low-level operation).

        Caller is responsible for enforcing business rules.

        Args:
            serial_number (str): Book identifier.
            is_borrowed (bool): Borrow state flag.
            borrower_card (Optional[str]): Borrower's card (if borrowed).
            borrowed_at (Optional[datetime]): Borrow timestamp.

        Returns:
            Optional[Book]: Updated book, or None if not found.
        """
        stmt = (
            update(Book)
            .where(Book.serial_number == serial_number)
            .values(
                is_borrowed=is_borrowed,
                borrower_card=borrower_card,
                borrowed_at=borrowed_at,
                updated_at=func.now(),
            )
            .returning(Book)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import Conflict, NotFound
from app.models.book import Book
from app.repositories.books import BookRepository
from app.schemas.books import BookCreate


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BookService:
    """Business logic for books. Stateless; operates per-session."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = BookRepository(session)

    # --- Commands -----------------------------------------------------------

    async def add_book(self, data: BookCreate) -> Book:
        # Existence check
        existing = await self.repo.get_by_serial(data.serial_number)
        if existing:
            raise Conflict("Book with this serial_number already exists.")

        obj = await self.repo.create(
            serial_number=data.serial_number,
            title=data.title,
            author=data.author,
        )
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def remove_book(self, serial_number: str) -> None:
        # Enforce policy: cannot delete when borrowed
        obj = await self.repo.get_for_update(serial_number)
        if obj is None:
            raise NotFound("Book not found.")

        if obj.is_borrowed:
            raise Conflict("Cannot delete a borrowed book. Return it first.")

        await self.repo.delete(serial_number)
        await self.session.commit()

    async def borrow_book(self, serial_number: str, borrower_card: str) -> Book:
        # Lock the row to serialize concurrent borrows
        obj = await self.repo.get_for_update(serial_number)
        if obj is None:
            raise NotFound("Book not found.")

        if obj.is_borrowed:
            # Idempotency: borrowing again by the same card returns 200 OK
            if obj.borrower_card == borrower_card:
                return obj
            raise Conflict("Book is already borrowed.")

        updated = await self.repo.update_borrow_state(
            serial_number=serial_number,
            is_borrowed=True,
            borrower_card=borrower_card,
            borrowed_at=utcnow(),
        )
        if updated is None:
            # Shouldn't happen due to prior fetch, but keep a guard
            raise NotFound("Book not found.")

        await self.session.commit()
        return updated

    async def return_book(self, serial_number: str) -> Book:
        # Lock the row to serialize concurrent returns/borrows
        obj = await self.repo.get_for_update(serial_number)
        if obj is None:
            raise NotFound("Book not found.")

        if not obj.is_borrowed:
            raise Conflict("Book is not currently borrowed.")

        updated = await self.repo.update_borrow_state(
            serial_number=serial_number,
            is_borrowed=False,
            borrower_card=None,
            borrowed_at=None,
        )
        if updated is None:
            raise NotFound("Book not found.")

        await self.session.commit()
        return updated

    # --- Queries ------------------------------------------------------------

    async def list_books(
        self,
        *,
        is_borrowed: Optional[bool] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[Iterable[Book], int]:
        # Clamp pagination
        limit = max(1, min(limit, 200))
        offset = max(0, offset)
        items, total = await self.repo.list(
            is_borrowed=is_borrowed,
            title=title,
            author=author,
            limit=limit,
            offset=offset,
        )
        return items, total

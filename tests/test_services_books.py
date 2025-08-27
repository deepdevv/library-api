import pytest
from datetime import datetime, timezone

from app.services.books import BookService
from app.schemas.books import BookCreate
from app.common.exceptions import Conflict, NotFound


@pytest.mark.asyncio
async def test_add_and_get_book(db_session):
    service = BookService(db_session)

    book_in = BookCreate(serial_number="123456", title="Test", author="Author")
    book = await service.add_book(book_in)
    assert book.serial_number == "123456"
    assert book.is_borrowed is False

    # Adding again should raise conflict
    with pytest.raises(Conflict):
        await service.add_book(book_in)


@pytest.mark.asyncio
async def test_remove_book(db_session):
    service = BookService(db_session)

    book_in = BookCreate(serial_number="111111", title="Removable", author="X")
    await service.add_book(book_in)

    # Removing works when not borrowed
    await service.remove_book("111111")

    # Removing again raises NotFound
    with pytest.raises(NotFound):
        await service.remove_book("111111")


@pytest.mark.asyncio
async def test_remove_borrowed_book_conflict(db_session):
    service = BookService(db_session)

    book_in = BookCreate(serial_number="222222", title="Borrowed", author="X")
    await service.add_book(book_in)

    # Borrow first
    await service.borrow_book("222222", "654321")

    # Now delete should conflict
    with pytest.raises(Conflict):
        await service.remove_book("222222")


@pytest.mark.asyncio
async def test_borrow_and_return_book(db_session):
    service = BookService(db_session)

    book_in = BookCreate(serial_number="333333", title="BorrowMe", author="Y")
    await service.add_book(book_in)

    # Borrow it
    b1 = await service.borrow_book("333333", "111111")
    assert b1.is_borrowed
    assert b1.borrower_card == "111111"
    assert isinstance(b1.borrowed_at, datetime)

    # Borrow again by same card is idempotent
    b2 = await service.borrow_book("333333", "111111")
    assert b2.borrower_card == "111111"

    # Borrow by different card conflicts
    with pytest.raises(Conflict):
        await service.borrow_book("333333", "222222")

    # Return it
    r1 = await service.return_book("333333")
    assert not r1.is_borrowed
    assert r1.borrower_card is None

    # Returning again conflicts
    with pytest.raises(Conflict):
        await service.return_book("333333")


@pytest.mark.asyncio
async def test_list_books(db_session):
    service = BookService(db_session)

    # Add 3 books
    for sn in ["444444", "555555", "666666"]:
        await service.add_book(BookCreate(serial_number=sn, title=f"T{sn}", author="A"))

    items, total = await service.list_books(limit=2, offset=0)
    assert total >= 3
    assert len(items) == 2

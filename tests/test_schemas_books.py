import pytest
from datetime import datetime, timezone

from app.schemas.books import (
    BookCreate,
    BookRead,
    BookStatusUpdate,
)

from pydantic import TypeAdapter
from app.schemas.books import BookStatusUpdate


class DummyBook:
    """Simple stand-in for an ORM object with attributes."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


# --- BookCreate --------------------------------------------------------------

def test_book_create_valid_trims_and_accepts_leading_zeros():
    b = BookCreate(serial_number="000001", title="  Title  ", author="  Author  ")
    assert b.serial_number == "000001"
    assert b.title == "Title"
    assert b.author == "Author"


@pytest.mark.parametrize("bad", ["12345", "1234567", "12 3456", "ABC123", ""])
def test_book_create_rejects_bad_serial_numbers(bad: str):
    with pytest.raises(Exception):
        BookCreate(serial_number=bad, title="T", author="A")


@pytest.mark.parametrize("title,author", [("   ", "A"), ("T", "  ")])
def test_book_create_rejects_empty_after_trim(title, author):
    with pytest.raises(Exception):
        BookCreate(serial_number="123456", title=title, author=author)


# --- BookStatusUpdate (discriminated union) ---------------------------------

def test_status_update_borrow_valid():
    payload = {"action": "borrow", "borrower_card": "654321"}
    ta = TypeAdapter(BookStatusUpdate)
    upd = ta.validate_python(payload)
    assert upd.action == "borrow"  # type: ignore[attr-defined]


def test_status_update_borrow_missing_card_rejected():
    payload = {"action": "borrow"}
    with pytest.raises(Exception):
        BookStatusUpdate.model_validate(payload)


@pytest.mark.parametrize("bad", ["", "65432", "6543210", "65 4321", "ABCDEF"])
def test_status_update_borrow_bad_card_rejected(bad):
    payload = {"action": "borrow", "borrower_card": bad}
    with pytest.raises(Exception):
        BookStatusUpdate.model_validate(payload)


def test_status_update_return_valid_and_forbids_extras():
    ok = {"action": "return"}
    ta = TypeAdapter(BookStatusUpdate)
    upd = ta.validate_python(ok)
    assert upd.action == "return"  # type: ignore[attr-defined]

    bad = {"action": "return", "borrower_card": "123456"}
    with pytest.raises(Exception):
        BookStatusUpdate.model_validate(bad)


# --- BookRead from attributes -----------------------------------------------

def test_book_read_from_attributes_and_validation_of_card():
    now = datetime.now(timezone.utc)
    obj = DummyBook(
        serial_number="123456",
        title="T",
        author="A",
        is_borrowed=True,
        borrowed_at=now,
        borrower_card="654321",
        created_at=now,
        updated_at=now,
    )

    out = BookRead.model_validate(obj)
    assert out.serial_number == "123456"
    assert out.is_borrowed is True
    assert out.borrower_card == "654321"
    assert out.borrowed_at == now

    # Bad borrower_card should raise
    obj_bad = DummyBook(
        serial_number="123456",
        title="T",
        author="A",
        is_borrowed=True,
        borrowed_at=now,
        borrower_card="abc123",
        created_at=now,
        updated_at=now,
    )
    with pytest.raises(Exception):
        BookRead.model_validate(obj_bad)

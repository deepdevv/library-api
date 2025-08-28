"""ORM model for the `books` table.

Defines columns, constraints, and indexes for managing library books.
"""


from sqlalchemy import Boolean, CheckConstraint, Column, Index, Text, CHAR, TIMESTAMP, func
from app.db.base import Base

class Book(Base):
    """Represents a library book.

    Columns:
        serial_number (CHAR[6]): Primary key, must be exactly six digits.
        title (Text): Book title (non-empty).
        author (Text): Book author (non-empty).
        is_borrowed (bool): Whether the book is currently borrowed.
        borrower_card (CHAR[6] | None): Borrower's card number, required when borrowed.
        borrowed_at (datetime | None): Timestamp when the book was borrowed.
        created_at (datetime): Creation timestamp (set by DB).
        updated_at (datetime): Last update timestamp (set by DB).

    Constraints:
        - serial_number must be six digits.
        - borrower_card must be six digits or null.
        - borrow state consistency:
            * if not borrowed → borrower_card and borrowed_at must be NULL.
            * if borrowed → borrower_card must be valid and borrowed_at not NULL.

    Indexes:
        - `idx_books_is_borrowed` on `is_borrowed` for efficient filtering.
    """
    __tablename__ = "books"

    serial_number = Column(CHAR(6), primary_key=True)

    title = Column(Text, nullable=False)
    author = Column(Text, nullable=False)

    is_borrowed = Column(Boolean, nullable=False, default=False, server_default="false")
    borrower_card = Column(CHAR(6), nullable=True)
    borrowed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        # format checks
        CheckConstraint(
            r"serial_number ~ '^[0-9]{6}$'", 
            name="serial_number_six_digits"
        ),
        CheckConstraint(
            r"borrower_card IS NULL OR borrower_card ~ '^[0-9]{6}$'", 
            name="borrower_card_six_digits_or_null"
        ),
        # borrow/return consistency
        CheckConstraint(
            "("
            " (is_borrowed = false AND borrower_card IS NULL AND borrowed_at IS NULL)"
            " OR "
            " (is_borrowed = true  AND borrower_card ~ '^[0-9]{6}$' AND borrowed_at IS NOT NULL)"
            ")",
            name="borrow_state_consistency",
        ),
        Index("idx_books_is_borrowed", "is_borrowed"),
    )

from sqlalchemy import Boolean, CheckConstraint, Column, Index, Text, CHAR, TIMESTAMP, func
from app.db.base import Base

class Book(Base):
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

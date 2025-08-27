import re
from datetime import datetime
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Shared regex (compiled once)
SIX_DIGIT_RE = re.compile(r"^\d{6}$")


class BookCreate(BaseModel):
    """Request model: create a new book (always created as available)."""

    serial_number: str = Field(
        ...,
        description="Exactly six digits, kept as a string to preserve leading zeros.",
        examples=["001234"],
    )
    title: str = Field(..., description="Non-empty title.", examples=["The Pragmatic Programmer"])
    author: str = Field(..., description="Non-empty author name.", examples=["Andrew Hunt"])

    # Trim whitespace on title/author and ensure not empty after trim
    @field_validator("title", "author", mode="before")
    @classmethod
    def _strip_and_require_non_empty(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v

    # Enforce exactly six digits for serial number
    @field_validator("serial_number")
    @classmethod
    def _validate_serial(cls, v: str) -> str:
        if not SIX_DIGIT_RE.fullmatch(v):
            raise ValueError("must be exactly six digits")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"serial_number": "001234", "title": "Clean Code", "author": "Robert C. Martin"}
            ]
        }
    )


class BookRead(BaseModel):
    """Response model: full book representation."""

    serial_number: str = Field(..., description="Six-digit string identifier.")
    title: str
    author: str
    is_borrowed: bool
    borrowed_at: Optional[datetime] = Field(
        None, description="Timestamp in UTC when the book was borrowed (null if available)."
    )
    borrower_card: Optional[str] = Field(
        None, description="Six-digit string of borrower's library card (null if available)."
    )
    created_at: datetime
    updated_at: datetime

    # If API returns borrower_card, ensure it's in the expected format when present
    @field_validator("borrower_card")
    @classmethod
    def _validate_card_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not SIX_DIGIT_RE.fullmatch(v):
            raise ValueError("must be exactly six digits")
        return v

    # Allow creation from SQLAlchemy ORM objects via attribute access
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "serial_number": "123456",
                    "title": "Clean Architecture",
                    "author": "Robert C. Martin",
                    "is_borrowed": False,
                    "borrowed_at": None,
                    "borrower_card": None,
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:00:00Z",
                }
            ]
        },
    )


# Discriminated union for PATCH /status
class _BorrowAction(BaseModel):
    action: Literal["borrow"] = Field("borrow", description="Borrow the book.")
    borrower_card: str = Field(..., description="Six-digit library card number.", examples=["654321"])

    @field_validator("borrower_card")
    @classmethod
    def _validate_card(cls, v: str) -> str:
        if not SIX_DIGIT_RE.fullmatch(v):
            raise ValueError("must be exactly six digits")
        return v

    # Do not allow any extra keys (e.g., borrowed_at, is_borrowed, etc.)
    model_config = ConfigDict(extra="forbid")


class _ReturnAction(BaseModel):
    action: Literal["return"] = Field("return", description="Return the book.")

    # Do not allow any extra keys on return either
    model_config = ConfigDict(extra="forbid")


BookStatusUpdate = Annotated[
    Union[_BorrowAction, _ReturnAction], Field(discriminator="action")
]
"""
Request model: update borrow status.

Examples:
- {"action": "borrow", "borrower_card": "654321"}
- {"action": "return"}
"""

class BookListResponse(BaseModel):
    items: list[BookRead]
    total: int = Field(..., ge=0, description="Total number of matching books.")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [
                        {
                            "serial_number": "000001",
                            "title": "Test",
                            "author": "Author",
                            "is_borrowed": False,
                            "borrowed_at": None,
                            "borrower_card": None,
                            "created_at": "2024-01-01T12:00:00Z",
                            "updated_at": "2024-01-01T12:00:00Z",
                        }
                    ],
                    "total": 1,
                }
            ]
        }
    )

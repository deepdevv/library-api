"""API routes for managing books.

This router exposes endpoints for CRUD operations and borrow/return workflows:
- Create a book
- Delete a book
- List books with optional filters
- Update borrow/return status
"""


from typing import Optional

from fastapi import APIRouter, Depends, status, Response

from app.api.deps import get_book_service
from app.schemas.books import (
    BookCreate,
    BookRead,
    BookListResponse,
    BookStatusUpdate,
)
from app.services.books import BookService

router = APIRouter(prefix="/books", tags=["books"])


@router.post(
    "",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new book",
    response_description="The created book",
)
async def create_book(
    data: BookCreate,
    response: Response,
    service: BookService = Depends(get_book_service),
) -> BookRead:
    """Add a new book to the catalog.

    Args:
        data (BookCreate): Book payload including serial number, title, and author.
        response (Response): Used to set the `Location` header for the created book.
        service (BookService): Service layer dependency.

    Returns:
        BookRead: The created book resource.

    Raises:
        Conflict: If a book with the same serial number already exists.
    """
    book = await service.add_book(data)
    response.headers["Location"] = f"/api/v1/books/{book.serial_number}"
    return BookRead.model_validate(book)


@router.delete(
    "/{serial_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a book",
)
async def delete_book(
    serial_number: str,
    service: BookService = Depends(get_book_service),
) -> None:
    """Delete a book by serial number.

    Args:
        serial_number (str): Six-digit book identifier.
        service (BookService): Service layer dependency.

    Raises:
        NotFound: If the book does not exist.
        Conflict: If the book is currently borrowed.
    """
    await service.remove_book(serial_number)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "",
    response_model=BookListResponse,
    summary="List books",
    response_description="Paginated list of books",
)
async def list_books(
    is_borrowed: Optional[bool] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    service: BookService = Depends(get_book_service),
) -> BookListResponse:
    """Retrieve a paginated list of books.

    Args:
        is_borrowed (Optional[bool]): Filter by borrow status.
        title (Optional[str]): Case-insensitive substring filter on title.
        author (Optional[str]): Case-insensitive substring filter on author.
        limit (int): Maximum number of items to return (default: 50).
        offset (int): Offset for pagination (default: 0).
        service (BookService): Service layer dependency.

    Returns:
        BookListResponse: Paginated list of books and total count.
    """
    items, total = await service.list_books(
        is_borrowed=is_borrowed,
        title=title,
        author=author,
        limit=limit,
        offset=offset,
    )
    return BookListResponse(items=[BookRead.model_validate(b) for b in items], total=total)


@router.patch(
    "/{serial_number}/status",
    response_model=BookRead,
    summary="Update borrow/return status",
    response_description="The updated book",
)
async def update_book_status(
    serial_number: str,
    action: BookStatusUpdate,
    service: BookService = Depends(get_book_service),
) -> BookRead:
    """Borrow or return a book depending on the requested action.

    Args:
        serial_number (str): Six-digit book identifier.
        action (BookStatusUpdate): Discriminated union payload with action type.
        service (BookService): Service layer dependency.

    Returns:
        BookRead: The updated book resource.

    Example payloads:
        - `{"action": "borrow", "borrower_card": "123456"}`
        - `{"action": "return"}`
    """
    if action.action == "borrow":
        book = await service.borrow_book(serial_number, action.borrower_card)
    else:
        book = await service.return_book(serial_number)

    return BookRead.model_validate(book)

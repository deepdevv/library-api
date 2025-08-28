"""Custom exception handlers for the Library API.

This module centralizes how domain-specific exceptions are converted
into structured JSON error responses with appropriate HTTP status codes.
"""


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.common.exceptions import NotFound, Conflict, ValidationError


def add_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI app.

    Handlers:
        - NotFound → HTTP 404 with `{"error": {"code": "not_found", ...}}`
        - Conflict → HTTP 409 with `{"error": {"code": "conflict", ...}}`
        - ValidationError → HTTP 422 with `{"error": {"code": "validation_error", ...}}`

    Args:
        app (FastAPI): Application instance to register handlers on.
    """

    @app.exception_handler(NotFound)
    async def not_found_handler(_: Request, exc: NotFound) -> JSONResponse:
        """Convert NotFound exceptions into HTTP 404 responses."""
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": exc.message, "details": {}}},
        )

    @app.exception_handler(Conflict)
    async def conflict_handler(_: Request, exc: Conflict) -> JSONResponse:
        """Convert Conflict exceptions into HTTP 409 responses."""
        return JSONResponse(
            status_code=409,
            content={"error": {"code": "conflict", "message": exc.message, "details": {}}},
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(_: Request, exc: ValidationError) -> JSONResponse:
        """Convert ValidationError exceptions into HTTP 422 responses."""
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "validation_error", "message": exc.message, "details": {}}},
        )

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.common.exceptions import NotFound, Conflict, ValidationError


def add_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI app."""

    @app.exception_handler(NotFound)
    async def not_found_handler(_: Request, exc: NotFound) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": exc.message, "details": {}}},
        )

    @app.exception_handler(Conflict)
    async def conflict_handler(_: Request, exc: Conflict) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"error": {"code": "conflict", "message": exc.message, "details": {}}},
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "validation_error", "message": exc.message, "details": {}}},
        )

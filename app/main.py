"""Application entrypoint and FastAPI app factory for the Library API.

This module exposes `create_app()` which wires routers, system endpoints,
and global exception handlers, and it instantiates the ASGI `app`.
"""

from fastapi import FastAPI

from app.api.routers import books
from app.common.error_handlers import add_exception_handlers


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Sets metadata, mounts API routers under `/api/v1`, registers the `/health`
    liveness endpoint, and attaches global exception handlers.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    app = FastAPI(
        title="Library API",
        version="1.0.0",
        description="Simple library system API for managing books",
    )

    # Routers
    app.include_router(books.router, prefix="/api/v1", tags=["books"])

    # Health endpoint
    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        """Liveness probe endpoint used by monitors/orchestrators."""
        return {"status": "ok"}

    # Register error handlers
    add_exception_handlers(app)

    return app


app = create_app()

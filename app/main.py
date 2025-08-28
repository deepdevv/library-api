from fastapi import FastAPI

from app.api.routers import books
from app.common.error_handlers import add_exception_handlers


def create_app() -> FastAPI:
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
        return {"status": "ok"}

    # Register error handlers
    add_exception_handlers(app)

    return app


app = create_app()

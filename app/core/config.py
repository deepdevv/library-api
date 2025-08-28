"""Application configuration and environment settings.

This module defines the `Settings` class, which centralizes environment-driven
configuration according to 12-factor app principles. Settings are loaded via
`pydantic-settings` and support both `.env` files and environment variables.
"""


from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration (12-factor).

    Supports two ways of configuring the database:
      - Direct `DATABASE_URL` (async DSN)
      - Individual `POSTGRES_*` pieces (DB, user, password, host, port)
        which are combined into an async DSN.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",   
        case_sensitive=False,
    )

    DATABASE_URL: Optional[str] = None

    POSTGRES_DB: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"

    def get_async_database_url(self) -> str:
        """Return the async PostgreSQL DSN to use.

        Priority:
            1. Use `DATABASE_URL` if provided.
            2. Otherwise, construct a DSN from POSTGRES_* pieces.

        Returns:
            str: Async PostgreSQL DSN (for use with async drivers).

        Raises:
            ValueError: If neither DATABASE_URL nor required POSTGRES_* vars are set.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if not all([self.POSTGRES_DB, self.POSTGRES_USER, self.POSTGRES_PASSWORD]):
            raise ValueError(
                "DATABASE_URL is missing and POSTGRES_DB/USER/PASSWORD are not fully set."
            )
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()

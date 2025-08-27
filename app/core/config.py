from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration (12-factor).
    Accepts either DATABASE_URL (async) or POSTGRES_* pieces and builds the async DSN.
    """

    # pydantic-settings v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # 👈 ignore unknown env vars
        case_sensitive=False,
    )

    # Direct DSN (async): e.g. postgresql+asyncpg://user:pass@host:port/db
    DATABASE_URL: Optional[str] = None

    # Optional pieces to build DSN if DATABASE_URL is not provided
    POSTGRES_DB: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Misc app settings
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"

    def get_async_database_url(self) -> str:
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


# Singleton-style instance
settings = Settings()

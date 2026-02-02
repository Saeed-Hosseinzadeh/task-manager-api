from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.

    Attributes:
        PROJECT_NAME: The name of the application.
        VERSION: The current application version.
        ENVIRONMENT: The runtime environment.
        DATABASE_URL: Database connection string.
        SECRET_KEY: Secret key used for JWT signing.
        ALGORITHM: JWT signing algorithm.
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration time in minutes.
        REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiration time in days.
        ALLOWED_ORIGINS: List of allowed CORS origins.
    """

    # --- Project Metadata ---
    PROJECT_NAME: str = "Task Manager API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "production", "test"] = "development"

    # --- Database Configuration ---
    DATABASE_URL: str = Field(..., description="Database connection URL")

    # --- Security & JWT ---
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, gt=0)

    # --- CORS Settings ---
    ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    # --- Configuration Source ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    Returns:
        Settings: The application settings object.
    """
    return Settings()


settings = get_settings()

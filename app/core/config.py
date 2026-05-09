"""
Application Configuration Module

This module defines the centralized configuration system used by the
application. Settings are loaded from environment variables and an
optional `.env` file using Pydantic's settings management.

Purpose
-------
Provide a single, strongly-typed configuration object that can be
safely imported and reused across the entire application.

Configuration Categories
------------------------
- Project metadata
- Database connection settings
- Security and JWT configuration
- CORS policy configuration

Loading Strategy
----------------
Settings are automatically loaded from:

1. Environment variables
2. `.env` file located at the project root

Environment variables always take precedence over `.env` values.

Performance
-----------
The settings instance is cached using `functools.lru_cache` to ensure
that configuration values are loaded only once during the application's
lifecycle.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Strongly-typed application configuration.

    This class defines all configuration parameters required by the
    application. Values are automatically populated from environment
    variables or the `.env` file.

    Sections
    --------
    Project Metadata
        General information about the running application.

    Database Configuration
        Connection parameters used by the database layer.

    Security & JWT
        Parameters required for token signing and authentication.

    CORS Settings
        Cross-Origin Resource Sharing configuration used by the API.

    Attributes
    ----------
    PROJECT_NAME : str
        Human-readable name of the application.

    VERSION : str
        Current application version.

    ENVIRONMENT : Literal["development", "production", "test"]
        Runtime environment identifier.

    DATABASE_URL : str
        Database connection string used by the ORM.

    SECRET_KEY : str
        Cryptographic key used for signing JWT tokens.

    ALGORITHM : str
        JWT signing algorithm.

    ACCESS_TOKEN_EXPIRE_MINUTES : int
        Lifetime of access tokens in minutes.

    REFRESH_TOKEN_EXPIRE_DAYS : int
        Lifetime of refresh tokens in days.

    ALLOWED_ORIGINS : list[str]
        List of allowed origins for CORS requests.
    """

    # --- Project Metadata ---
    PROJECT_NAME: str = "Task Manager API"
    VERSION: str = "1.0.0"

    # Defines the runtime environment for the application.
    ENVIRONMENT: Literal["development", "production", "test"] = "development"

    # --- Database Configuration ---

    # Database connection string used by the persistence layer.
    DATABASE_URL: str = Field(..., description="Database connection URL")

    # --- Security & JWT Configuration ---

    # Secret key used to sign and verify JWT tokens.
    SECRET_KEY: str = Field(..., min_length=32)

    # JWT signing algorithm.
    ALGORITHM: str = "HS256"

    # Access token lifetime (minutes).
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, gt=0)

    # Refresh token lifetime (days).
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, gt=0)

    # --- CORS Configuration ---

    # List of allowed origins for cross-origin requests.
    ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    # --- Settings Source Configuration ---
    model_config = SettingsConfigDict(
        env_file=".env",              # Load variables from .env file
        env_file_encoding="utf-8",    # File encoding
        case_sensitive=True,          # Environment variable names are case-sensitive
        extra="ignore",               # Ignore undefined environment variables
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached instance of the application settings.

    The `lru_cache` decorator ensures that the configuration is loaded
    only once during the application's lifecycle, preventing repeated
    environment parsing and improving performance.

    Returns
    -------
    Settings
        The initialized and cached application settings object.
    """
    return Settings()


# Global settings instance used across the application.
# Import this object wherever configuration access is required.
settings = get_settings()

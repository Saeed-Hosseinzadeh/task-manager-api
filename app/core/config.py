from typing import Literal
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings. Values are loaded from environment variables.
    Defaults are used only for development/testing contexts.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        hide_input_in_errors=True
    )

    PROJECT_NAME: str = "Task Manager API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "production", "test"] = "development"

    # Database settings
    DATABASE_URL: str

    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, gt=0)

    # CORS
    ALLOWED_ORIGINS: list[str] = Field(default_factory=list)

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
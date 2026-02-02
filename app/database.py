from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from collections.abc import Generator

from app.core.config import settings


# Database URL loaded from environment variables
SQLALCHEMY_DATABASE_URL: str = settings.DATABASE_URL


# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,   # Prevents stale connections
    future=True           # Enables SQLAlchemy 2.0 style usage
)


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Ensures proper opening and closing of the session.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

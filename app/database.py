"""
Database Configuration

This module handles the SQLAlchemy database engine setup, session factory creation,
and base model declaration, along with a dependency for database session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from collections.abc import Generator

from app.core.config import settings


# Database URL loaded from environment variables
SQLALCHEMY_DATABASE_URL: str = settings.DATABASE_URL


# Create SQLAlchemy engine
# pool_pre_ping=True: Prevents stale connections by checking connectivity
# future=True: Enables SQLAlchemy 2.0 style usage
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    future=True
)


# Session factory for creating new database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields:
        Session: An active SQLAlchemy database session.

    Ensures the database session is properly closed after the request is processed,
    regardless of whether the request was successful or raised an exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

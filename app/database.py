from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# SQLAlchemy Engine Configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,      # Verify connections on checkout
    pool_size=10,            # Adjust based on traffic needs
    max_overflow=20,         # Allow temporary spikes
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

def get_db() -> Generator:
    """Dependency for API endpoints to handle DB session lifecycle."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()
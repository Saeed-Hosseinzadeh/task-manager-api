from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Generator
from app.core.config import settings

database_url = make_url(settings.DATABASE_URL)
engine_options = {"pool_size": 10, "max_overflow": 20}
if database_url.get_backend_name() == "sqlite":
    engine_options["connect_args"] = {"check_same_thread": False}
    if database_url.database in (None, "", ":memory:"):
        engine_options = {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }

engine = create_engine(database_url, pool_pre_ping=True, hide_parameters=True, **engine_options)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as db:
        yield db

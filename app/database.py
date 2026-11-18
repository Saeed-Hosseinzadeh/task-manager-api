from collections.abc import Generator
from typing import TypedDict

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


class EngineOptions(TypedDict, total=False):
    pool_size: int
    max_overflow: int
    connect_args: dict[str, bool]
    poolclass: type[StaticPool]


database_url = make_url(settings.DATABASE_URL)
engine_options: EngineOptions = {"pool_size": 10, "max_overflow": 20}
if database_url.get_backend_name() == "sqlite":
    engine_options["connect_args"] = {"check_same_thread": False}
    if database_url.database in (None, "", ":memory:"):
        engine_options = {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }

engine = create_engine(database_url, pool_pre_ping=True, hide_parameters=True, **engine_options)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as db:
        yield db

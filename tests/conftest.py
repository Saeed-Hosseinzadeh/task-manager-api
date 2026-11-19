import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def db_session():
    """Give each test its own in-memory database, including committed writes."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql("PRAGMA foreign_keys = ON")
            Base.metadata.create_all(connection)
        with Session(engine, autoflush=False) as session:
            yield session
    finally:
        engine.dispose()


@pytest.fixture
def client(db_session, monkeypatch):
    """
    Provides a FastAPI TestClient with the database dependency overridden.
    """

    def override_get_db():
        yield db_session

    monkeypatch.setitem(app.dependency_overrides, get_db, override_get_db)

    with TestClient(app) as test_client:
        yield test_client

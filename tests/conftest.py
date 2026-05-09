"""
API Testing Configuration

This module defines shared pytest fixtures used for integration
testing of the FastAPI application.

Purpose
-------
Provide a fully isolated testing environment by replacing the
application's database dependency with an in-memory SQLite database.

Testing Design
--------------
- Use an in-memory SQLite database for fast execution.
- Create the database schema once per test session.
- Use database transactions to isolate each test case.
- Override FastAPI dependency injection to supply the test session.

Fixtures
--------
setup_database
    Initializes and removes database tables for the test session.

db_session
    Provides a transactional SQLAlchemy session for each test.

client
    Provides a FastAPI TestClient configured to use the test database.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


# Database connection string used only for tests.
# SQLite in-memory mode ensures fast execution and no persistent state.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


# Create a SQLAlchemy engine configured for the in-memory database.
# The `check_same_thread=False` option allows usage across threads
# which is required when interacting with FastAPI's TestClient.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# Session factory used to generate database sessions during tests.
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="session")
def setup_database():
    """
    Create and destroy database schema for the test session.

    All tables defined in SQLAlchemy metadata are created before
    tests begin and dropped after the entire test session completes.

    Scope
    -----
    session
        Executes once for the entire pytest session lifecycle.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(setup_database):
    """
    Provide an isolated database session for a single test.

    Each test receives a dedicated connection and transaction.
    After the test completes, the transaction is rolled back
    to ensure that database state does not leak between tests.

    This pattern guarantees deterministic test results.
    """
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """
    Create a FastAPI TestClient configured with the test database.

    This fixture overrides the application's `get_db` dependency
    so that all database operations during tests use the isolated
    testing session.

    Returns
    -------
    TestClient
        A configured FastAPI TestClient instance for executing
        HTTP requests against the application during tests.
    """

    def override_get_db():
        yield db_session

    # Inject the testing database session into FastAPI dependencies.
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Remove dependency overrides after the test completes.
    app.dependency_overrides.clear()

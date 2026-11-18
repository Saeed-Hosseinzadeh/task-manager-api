"""Use Alembic-managed schemas on an explicitly configured test PostgreSQL server."""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.database import get_db
from app.main import app

pytestmark = pytest.mark.postgresql
INITIAL_REVISION = "9aa2a41540d5"
LONG_EMAIL = "a" * 58 + "@" + "b" * 50 + ".example.org"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def postgres_schema():
    database_url = os.environ.get("POSTGRES_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set POSTGRES_TEST_DATABASE_URL to a disposable PostgreSQL database")
    base_url = make_url(database_url)
    if base_url.get_backend_name() != "postgresql":
        pytest.fail("POSTGRES_TEST_DATABASE_URL must point to PostgreSQL")

    schema = f"task_test_{uuid4().hex}"
    base_engine = create_engine(base_url)
    scoped_url = base_url.update_query_dict(
        {"options": f"-csearch_path={schema} -ctimezone=Asia/Tokyo"}
    )
    engine = create_engine(scoped_url)
    try:
        with base_engine.begin() as connection:
            connection.execute(text(f"CREATE SCHEMA {schema}"))
        yield engine, scoped_url
    finally:
        engine.dispose()
        try:
            with base_engine.begin() as connection:
                connection.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        finally:
            base_engine.dispose()


def migrate(url, *args, check=True):
    return subprocess.run(
        [sys.executable, "-B", "-m", "alembic", *args],
        cwd=PROJECT_ROOT,
        env={**os.environ, "DATABASE_URL": url.render_as_string(hide_password=False)},
        check=check,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def postgres_client(postgres_schema, monkeypatch):
    engine, url = postgres_schema
    migrate(url, "upgrade", "head")
    migrate(url, "check")
    with migrated_api_client(engine, monkeypatch) as client:
        yield client


@contextmanager
def migrated_api_client(engine, monkeypatch):
    def override_db():
        with Session(engine) as session:
            yield session

    monkeypatch.setitem(app.dependency_overrides, get_db, override_db)
    with TestClient(app) as client:
        yield client


def register(client, username, email=None):
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email or f"{username}@example.org",
            "password": "integration-test-password",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_migrated_postgresql_task_crud_and_ownership(postgres_client):
    client = postgres_client
    owner = register(client, "owner", LONG_EMAIL)
    assert owner["email"] == LONG_EMAIL
    other = register(client, "other")
    owner_headers = auth(owner["access_token"])
    other_headers = auth(other["access_token"])

    assert client.get("/tasks/").status_code == 401
    assert client.get("/tasks/", headers=auth(owner["refresh_token"])).status_code == 401
    response = client.post("/tasks/", json={"title": "PostgreSQL task"}, headers=owner_headers)
    assert response.status_code == 201, response.text
    task = response.json()["data"]
    assert task["owner_id"] == owner["id"]
    assert datetime.fromisoformat(task["created_at"]).tzinfo is None
    assert task["is_completed"] is False
    assert task["priority"] == 1
    path = f"/tasks/{task['id']}"

    response = client.get("/tasks/", headers=owner_headers)
    assert response.status_code == 200
    assert response.json()["data"] == [task]
    response = client.get(path, headers=owner_headers)
    assert response.status_code == 200
    assert response.json()["data"] == task

    response = client.get("/tasks/", headers=other_headers)
    assert response.status_code == 200
    assert response.json()["data"] == []
    assert client.get(path, headers=other_headers).status_code == 404
    assert client.put(path, json={"title": "Other title"}, headers=other_headers).status_code == 404
    assert client.delete(path, headers=other_headers).status_code == 404

    response = client.put(path, json={"is_completed": True}, headers=owner_headers)
    assert response.status_code == 200
    assert response.json()["data"]["is_completed"] is True
    assert response.json()["data"]["title"] == task["title"]
    assert client.delete(path, headers=owner_headers).status_code == 200
    assert client.get(path, headers=owner_headers).status_code == 404
    assert client.get("/tasks/", headers=owner_headers).json()["data"] == []


def insert_legacy_owner(connection, email="legacy@example.org"):
    return connection.execute(
        text("""
        INSERT INTO users (username, email, hashed_password)
        VALUES ('legacy', :email, 'legacy-test-hash') RETURNING id
    """),
        {"email": email},
    ).scalar_one()


def test_legacy_data_upgrade_downgrade_and_reupgrade(postgres_schema, monkeypatch):
    engine, url = postgres_schema
    migrate(url, "upgrade", INITIAL_REVISION)
    with engine.begin() as connection:
        owner_id = insert_legacy_owner(connection, LONG_EMAIL)
        connection.execute(
            text("""
            INSERT INTO tasks (title, owner_id, created_at, due_date)
            VALUES ('Legacy nulls', :owner_id, NULL, NULL),
                   ('Legacy timestamp', :owner_id, '2020-01-02 03:04:05',
                    '2020-03-04 05:06:07')
        """),
            {"owner_id": owner_id},
        )

    with engine.begin() as connection:
        before_migration = connection.execute(
            text("SELECT clock_timestamp() AT TIME ZONE 'UTC'")
        ).scalar_one()
    migrate(url, "upgrade", "head")
    with engine.begin() as connection:
        after_migration = connection.execute(
            text("SELECT clock_timestamp() AT TIME ZONE 'UTC'")
        ).scalar_one()
        assert connection.execute(text("SHOW TimeZone")).scalar_one() == "Asia/Tokyo"
        assert connection.execute(text("SELECT email FROM users")).scalar_one() == LONG_EMAIL
        backfilled, preserved = (
            connection.execute(
                text("""
            SELECT created_at, due_date, is_completed, priority, owner_id
            FROM tasks ORDER BY id
        """)
            )
            .mappings()
            .all()
        )
        assert before_migration <= backfilled["created_at"] <= after_migration
        assert backfilled["due_date"] is None
        assert backfilled["is_completed"] is False
        assert backfilled["priority"] == 1
        assert backfilled["owner_id"] == owner_id
        assert preserved["created_at"] == datetime(2020, 1, 2, 3, 4, 5)
        assert preserved["due_date"] == datetime(2020, 3, 4, 5, 6, 7)

        defaults = connection.execute(
            text("""
            INSERT INTO tasks (title, owner_id) VALUES ('Defaults', :owner_id)
            RETURNING created_at, is_completed, priority
        """),
            {"owner_id": owner_id},
        ).one()
        utc_transaction_time = connection.execute(
            text("SELECT CURRENT_TIMESTAMP AT TIME ZONE 'UTC'")
        ).scalar_one()
        assert defaults.created_at == utc_transaction_time
        assert (defaults.is_completed, defaults.priority) == (False, 1)
        assert "ix_tasks_owner_id" in {
            index["name"] for index in inspect(connection).get_indexes("tasks")
        }

    with migrated_api_client(engine, monkeypatch) as client:
        headers = auth(create_access_token({"sub": str(owner_id)}))
        response = client.get("/tasks/", headers=headers)
        assert response.status_code == 200
        legacy = next(
            task for task in response.json()["data"] if task["title"] == "Legacy timestamp"
        )
        assert legacy["due_date"] == "2020-03-04T05:06:07"
        path = f"/tasks/{legacy['id']}"
        assert (
            client.put(path, json={"is_completed": True}, headers=headers).json()["data"][
                "due_date"
            ]
            == legacy["due_date"]
        )
        assert (
            client.put(path, json={"due_date": legacy["due_date"]}, headers=headers).status_code
            == 422
        )

    migrate(url, "downgrade", INITIAL_REVISION)
    with engine.begin() as connection:
        row = connection.execute(
            text("""
            SELECT created_at, due_date FROM tasks WHERE title = 'Legacy timestamp'
        """)
        ).one()
        assert row.created_at == datetime(2020, 1, 2, 3, 4, 5)
        assert row.due_date == datetime(2020, 3, 4, 5, 6, 7)
        assert connection.execute(text("SELECT count(*) FROM tasks")).scalar_one() == 3

    migrate(url, "upgrade", "head")
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM users WHERE id = :id"), {"id": owner_id})
        assert connection.execute(text("SELECT count(*) FROM tasks")).scalar_one() == 0


def test_new_deadlines_are_utc_and_block_lossy_downgrade(postgres_schema, monkeypatch):
    engine, url = postgres_schema
    migrate(url, "upgrade", "head")
    with migrated_api_client(engine, monkeypatch) as client:
        owner = register(client, "deadline-owner")
        headers = auth(owner["access_token"])
        payload = {"title": "New deadline", "due_date": "2026-11-18T15:30:00+03:30"}
        response = client.post("/tasks/", json=payload, headers=headers)
        assert response.status_code == 201, response.text
        task = response.json()["data"]
        assert task["due_date"] == "2026-11-18T12:00:00Z"
        path = f"/tasks/{task['id']}"
        assert client.get(path, headers=headers).json()["data"]["due_date"] == task["due_date"]
        assert (
            client.put(path, json={"due_date": "2026-11-19T04:00:00Z"}, headers=headers).status_code
            == 200
        )

        result = migrate(url, "downgrade", INITIAL_REVISION, check=False)
        assert result.returncode != 0
        assert "Downgrade would discard timezone-aware deadlines" in result.stderr
        with engine.begin() as connection:
            legacy, instant = connection.execute(
                text("SELECT due_date, due_date_instant FROM tasks")
            ).one()
            assert legacy is None
            assert instant == datetime(2026, 11, 19, 4, tzinfo=UTC)
            assert (
                connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                == "ef72b89db261"
            )

        cleared = client.put(path, json={"due_date": None}, headers=headers)
        assert cleared.status_code == 200
        assert cleared.json()["data"]["due_date"] is None

    migrate(url, "downgrade", INITIAL_REVISION)
    migrate(url, "upgrade", "head")


@pytest.mark.parametrize(
    ("title", "has_owner", "error"),
    [
        ("Owner missing", False, "Tasks without an owner"),
        ("x" * 151, True, "tasks.title exceeds the new length limit"),
    ],
)
def test_upgrade_rejects_ambiguous_legacy_data_without_changes(
    postgres_schema, title, has_owner, error
):
    engine, url = postgres_schema
    migrate(url, "upgrade", INITIAL_REVISION)
    with engine.begin() as connection:
        owner_id = insert_legacy_owner(connection) if has_owner else None
        connection.execute(
            text("INSERT INTO tasks (title, owner_id) VALUES (:title, :owner_id)"),
            {"title": title, "owner_id": owner_id},
        )

    result = migrate(url, "upgrade", "head", check=False)
    assert result.returncode != 0
    assert error in result.stderr
    with engine.begin() as connection:
        assert (
            connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            == INITIAL_REVISION
        )
        assert connection.execute(text("SELECT title, owner_id FROM tasks")).one() == (
            title,
            owner_id,
        )


def test_concurrent_registration_returns_conflict(postgres_client):
    barrier = Barrier(2)
    body = {
        "username": "concurrent",
        "email": "concurrent@example.org",
        "password": "synthetic-registration-password",
    }

    def submit():
        barrier.wait(timeout=5)
        return postgres_client.post("/auth/register", json=body)

    with ThreadPoolExecutor(max_workers=2) as pool:
        requests = [pool.submit(submit) for _ in range(2)]
        responses = [request.result() for request in requests]

    assert sorted(response.status_code for response in responses) == [201, 409]
    rejected = next(response for response in responses if response.status_code == 409)
    assert rejected.json()["success"] is False
    login = postgres_client.post(
        "/auth/login",
        json={
            "identifier": body["email"],
            "password": body["password"],
        },
    )
    assert login.status_code == 200

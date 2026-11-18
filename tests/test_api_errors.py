import pytest
from passlib.hash import pbkdf2_sha256
from sqlalchemy import delete
from sqlalchemy.exc import OperationalError

from app.models import User


def register(client, **overrides):
    body = {
        "username": "error-test",
        "email": "errors@example.org",
        "password": "synthetic-test-password",
        **overrides,
    }
    return client.post("/auth/register", json=body)


def assert_validation_error(response, field):
    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert any(error["field"] == field for error in payload["data"])


def test_registration_normalizes_before_validation(client):
    assert_validation_error(register(client, username=" x "), "username")
    invalid = register(client, password="12")
    assert_validation_error(invalid, "password")
    assert "input" not in invalid.json()["data"][0]

    first = register(client, username="  normalized  ")
    assert first.status_code == 201
    assert first.json()["data"]["username"] == "normalized"
    conflict = register(client, username="normalized")
    assert conflict.status_code == 409
    assert conflict.json()["success"] is False


@pytest.fixture
def registered(client):
    response = register(client)
    assert response.status_code == 201
    return response.json()["data"]


def test_task_validation_leaves_existing_task_intact(client, registered):
    headers = {"Authorization": f"Bearer {registered['access_token']}"}
    invalid = client.post("/tasks/", headers=headers, json={"title": " x "})
    assert_validation_error(invalid, "title")
    created = client.post("/tasks/", headers=headers, json={"title": " Valid title "})
    assert created.status_code == 201
    task = created.json()["data"]
    assert task["title"] == "Valid title"
    path = f"/tasks/{task['id']}"

    for field in ("title", "is_completed", "priority"):
        assert_validation_error(client.put(path, headers=headers, json={field: None}), field)
    assert_validation_error(client.get("/tasks/?sort_order=unknown", headers=headers), "sort_order")
    assert client.get(path, headers=headers).json()["data"] == task


def test_missing_credentials_and_deleted_account(client, db_session, registered):
    missing = client.get("/tasks/")
    assert missing.status_code == 401
    assert missing.headers["www-authenticate"] == "Bearer"
    assert missing.json()["success"] is False

    db_session.execute(delete(User).where(User.id == registered["id"]))
    db_session.commit()
    refresh = client.post("/auth/refresh", json={"refresh_token": registered["refresh_token"]})
    assert refresh.status_code == 401
    assert refresh.headers["www-authenticate"] == "Bearer"
    assert refresh.json()["success"] is False


def test_openapi_describes_bearer_and_validation_envelope(client):
    spec = client.get("/openapi.json").json()
    assert spec["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"
    operation = spec["paths"]["/tasks/"]["post"]
    assert {"HTTPBearer": []} in operation["security"]
    schema = operation["responses"]["422"]["content"]["application/json"]["schema"]
    assert schema["$ref"] == "#/components/schemas/ErrorResponse"


def test_invalid_login_has_generic_error(client, registered):
    for identifier in (registered["email"], "unknown@example.org"):
        response = client.post(
            "/auth/login",
            json={"identifier": identifier, "password": "incorrect-test-password"},
        )
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"
        assert response.json() == {
            "success": False,
            "message": "Invalid credentials",
            "data": None,
        }


def test_database_error_does_not_disclose_sql(client, db_session, registered, monkeypatch):
    def fail(*args, **kwargs):
        raise OperationalError(
            "synthetic SQL", {"value": "synthetic-private-value"}, RuntimeError()
        )

    monkeypatch.setattr(db_session, "query", fail)
    headers = {"Authorization": f"Bearer {registered['access_token']}"}
    response = client.get("/tasks/", headers=headers)
    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "message": "A database error occurred",
        "data": None,
    }


def test_task_list_paginates_and_filters_with_stable_order(client, registered):
    headers = {"Authorization": f"Bearer {registered['access_token']}"}
    task_ids = []
    for completed, priority in ((True, 3), (True, 3), (True, 2), (False, 3)):
        response = client.post(
            "/tasks/",
            headers=headers,
            json={"title": "Same title", "is_completed": completed, "priority": priority},
        )
        assert response.status_code == 201
        task_ids.append(response.json()["data"]["id"])

    params = {"completed": True, "priority": 3, "sort_by": "title", "limit": 1}
    for offset, expected in enumerate(([task_ids[0]], [task_ids[1]], [])):
        response = client.get("/tasks/", headers=headers, params={**params, "offset": offset})
        assert response.status_code == 200
        assert [task["id"] for task in response.json()["data"]] == expected

    for field, value in (("limit", 0), ("limit", 101), ("offset", -1), ("priority", 6)):
        assert_validation_error(
            client.get("/tasks/", headers=headers, params={field: value}), field
        )


def test_login_upgrades_legacy_password_hash(client, db_session, registered):
    user = db_session.get(User, registered["id"])
    user.hashed_password = pbkdf2_sha256.using(rounds=29_000).hash("synthetic-test-password")
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={
            "identifier": registered["email"],
            "password": "synthetic-test-password",
        },
    )
    assert response.status_code == 200
    db_session.refresh(user)
    assert pbkdf2_sha256.from_string(user.hashed_password).rounds == 600_000

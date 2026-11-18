import pytest


@pytest.fixture
def auth_headers(client):
    result = client.post(
        "/auth/register",
        json={
            "username": "deadline-user",
            "email": "deadline@example.org",
            "password": "deadline-test-password",
        },
    )
    assert result.status_code == 201
    return {"Authorization": f"Bearer {result.json()['data']['access_token']}"}


@pytest.mark.parametrize(
    "deadline",
    ["2026-11-18T15:30:00", 1795003200, "1795003200", "0001-01-01T00:00:00+01:00"],
)
def test_create_and_update_require_an_explicit_offset(client, auth_headers, deadline):
    rejected = client.post(
        "/tasks/", headers=auth_headers, json={"title": "Test deadline", "due_date": deadline}
    )
    assert rejected.status_code == 422
    assert any(error["field"] == "due_date" for error in rejected.json()["data"])
    created = client.post("/tasks/", headers=auth_headers, json={"title": "Test deadline"})
    assert created.status_code == 201
    path = f"/tasks/{created.json()['data']['id']}"
    assert client.put(path, headers=auth_headers, json={"due_date": deadline}).status_code == 422
    assert client.get(path, headers=auth_headers).json()["data"]["due_date"] is None


def test_deadline_round_trips_as_utc_and_can_be_cleared(client, auth_headers):
    created = client.post(
        "/tasks/",
        headers=auth_headers,
        json={"title": "Test deadline", "due_date": "2026-11-18T15:30:00+03:30"},
    )
    assert created.status_code == 201
    task = created.json()["data"]
    assert task["due_date"] == "2026-11-18T12:00:00Z"
    path = f"/tasks/{task['id']}"
    assert client.get(path, headers=auth_headers).json()["data"]["due_date"] == task["due_date"]

    unchanged = client.put(path, headers=auth_headers, json={"is_completed": True})
    assert unchanged.status_code == 200
    assert unchanged.json()["data"]["due_date"] == task["due_date"]

    cleared = client.put(path, headers=auth_headers, json={"due_date": None})
    assert cleared.status_code == 200
    assert cleared.json()["data"]["due_date"] is None

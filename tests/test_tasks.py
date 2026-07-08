def register_user(
    client,
    *,
    username: str = "taskuser",
    email: str = "task@example.com",
    password: str = "Test@123",
):
    return client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )


def login_user(client, *, identifier: str, password: str = "Test@123"):
    return client.post(
        "/auth/login",
        json={
            "identifier": identifier,
            "password": password,
        },
    )


def get_access_token(client) -> str:
    register_response = register_user(client)
    assert register_response.status_code == 201

    login_response = login_user(client, identifier="task@example.com")
    assert login_response.status_code == 200

    return login_response.json()["data"]["access_token"]


def test_create_task(client) -> None:
    access_token = get_access_token(client)

    response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "testing task",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 201

    payload = response.json()
    assert payload["success"] is True
    assert payload["message"]
    assert payload["data"]["id"] is not None
    assert payload["data"]["title"] == "Test Task"
    assert payload["data"]["description"] == "testing task"

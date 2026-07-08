def register_user(
    client,
    *,
    username: str = "ciuser",
    email: str = "ciuser@example.com",
    password: str = "Test@123456",
):
    return client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )


def login_user(client, *, identifier: str, password: str = "Test@123456"):
    return client.post(
        "/auth/login",
        json={
            "identifier": identifier,
            "password": password,
        },
    )


def get_auth_headers(client) -> dict[str, str]:
    register_response = register_user(client)
    assert register_response.status_code == 201

    login_response = login_user(client, identifier="ciuser@example.com")
    assert login_response.status_code == 200

    token = login_response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_ci_full_flow(client) -> None:
    headers = get_auth_headers(client)

    response = client.post(
        "/tasks",
        json={
            "title": "CI Task",
            "description": "Created during CI test",
        },
        headers=headers,
    )
    assert response.status_code == 201

    payload = response.json()
    assert payload["success"] is True
    assert payload["message"]
    assert payload["data"]["title"] == "CI Task"
    assert payload["data"]["description"] == "Created during CI test"


def test_health_check(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert payload["message"]

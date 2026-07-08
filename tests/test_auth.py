def register_user(
    client,
    *,
    username: str = "testuser",
    email: str = "test@example.com",
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


def test_register_user_success(client) -> None:
    response = register_user(client)

    assert response.status_code == 201

    payload = response.json()
    assert payload["success"] is True
    assert payload["message"]
    assert payload["data"]["id"] is not None
    assert payload["data"]["username"] == "testuser"
    assert payload["data"]["email"] == "test@example.com"


def test_register_then_login(client) -> None:
    register_response = register_user(
        client,
        username="loginuser",
        email="login@example.com",
    )
    assert register_response.status_code == 201

    login_response = login_user(
        client,
        identifier="login@example.com",
    )
    assert login_response.status_code == 200

    payload = login_response.json()
    assert payload["success"] is True
    assert payload["message"]
    assert payload["data"]["access_token"]
    assert payload["data"]["refresh_token"]
    assert payload["data"]["token_type"] == "bearer"

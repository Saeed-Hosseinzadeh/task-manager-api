def register_user(
    client,
    *,
    username: str = "flowuser",
    email: str = "flow@example.com",
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


def authenticate(client) -> dict[str, str]:
    register_response = register_user(client)
    assert register_response.status_code == 201

    login_response = login_user(client, identifier="flow@example.com")
    assert login_response.status_code == 200

    access_token = login_response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_full_user_flow(client) -> None:
    headers = authenticate(client)

    create_response = client.post(
        "/tasks",
        json={
            "title": "Integration Task",
            "description": "Testing full workflow",
        },
        headers=headers,
    )
    assert create_response.status_code == 201

    create_payload = create_response.json()
    assert create_payload["success"] is True
    assert create_payload["message"]
    assert create_payload["data"]["title"] == "Integration Task"

    list_response = client.get("/tasks", headers=headers)
    assert list_response.status_code == 200

    list_payload = list_response.json()
    assert list_payload["success"] is True
    assert list_payload["message"]
    assert isinstance(list_payload["data"], list)
    assert len(list_payload["data"]) == 1
    assert list_payload["data"][0]["title"] == "Integration Task"

def test_full_user_flow(client) -> None:
    """
    Test full user workflow:
    register -> login -> create task -> retrieve tasks.
    """

    # Register
    register_response = client.post(
        "/auth/register",
        json={
            "username": "flowuser",
            "email": "flow@example.com",
            "password": "Test@123"
        }
    )

    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/auth/login",
        json={
            "identifier": "flow@example.com",
            "password": "Test@123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create task
    create_response = client.post(
        "/tasks",
        json={
            "title": "Integration Task",
            "description": "Testing full workflow"
        },
        headers=headers
    )

    assert create_response.status_code == 201

    # Get tasks
    tasks_response = client.get(
        "/tasks",
        headers=headers
    )

    assert tasks_response.status_code == 200

    tasks_data = tasks_response.json()

    assert tasks_data["success"] is True
    assert len(tasks_data["data"]) >= 1

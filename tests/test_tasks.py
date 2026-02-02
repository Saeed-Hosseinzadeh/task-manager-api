def test_create_task(client) -> None:
    """
    Test authenticated user can create a new task successfully.

    Args:
        client: FastAPI test client fixture.

    Returns:
        None
    """
    login_response = client.post(
        "/auth/login",
        json={
            "identifier": "test@example.com",
            "password": "Test@123"
        }
    )

    assert login_response.status_code == 200, "Login request failed."

    token = login_response.json()["data"]["access_token"]

    create_response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "testing task"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert create_response.status_code == 201, "Task creation failed."

    response_data = create_response.json()

    assert response_data["success"] is True
    assert response_data["message"] is not None
    assert response_data["data"]["title"] == "Test Task"
    assert response_data["data"]["description"] == "testing task"

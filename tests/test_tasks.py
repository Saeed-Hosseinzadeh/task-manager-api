"""
Task API Tests

This module contains integration tests for task-related API endpoints.
The tests validate that authenticated users can perform operations
on task resources through the public API.

Testing Focus
-------------
- Authentication flow required for protected endpoints
- Task creation via `/tasks`
- Validation of API response structure and returned task data

The tests rely on the FastAPI TestClient and the isolated testing
database environment configured by pytest fixtures.
"""


def test_create_task(client) -> None:
    """
    Verify that an authenticated user can successfully create a task.

    Test Flow
    ---------
    1. Register a new user to ensure the account exists in the test database.
    2. Authenticate the user and retrieve the access token.
    3. Send a request to create a new task using the Authorization header.
    4. Validate the API response structure and returned task data.

    Parameters
    ----------
    client : TestClient
        FastAPI test client fixture configured with the testing database.

    Returns
    -------
    None
    """

    # Step 1: Register a user account required for authentication
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test@123"
        }
    )

    # Step 2: Authenticate the user to obtain an access token
    login_response = client.post(
        "/auth/login",
        json={
            "identifier": "test@example.com",
            "password": "Test@123"
        }
    )

    assert login_response.status_code == 200, "Login request failed."

    # The API responses are wrapped using a standardized success response format.
    # The authentication token is retrieved from the `data` field.
    token = login_response.json()["data"]["access_token"]

    # Step 3: Create a new task using the Authorization header
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

    # Step 4: Validate the response payload
    assert response_data["success"] is True
    assert response_data["message"] is not None
    assert response_data["data"]["title"] == "Test Task"
    assert response_data["data"]["description"] == "testing task"

"""
Authentication Continuous Integration Tests

This module contains integration tests designed to validate the
authentication workflow of the API within automated testing and
continuous integration environments.

Purpose
-------
Ensure that the core authentication flow works correctly from
an external API perspective, including:

- User registration
- User authentication
- Token issuance

The tests interact with the API using FastAPI's TestClient and rely
on the testing database environment provided by pytest fixtures.
"""


def test_register_user_success(client) -> None:
    """
    Validate successful user registration.

    This test verifies that the registration endpoint correctly
    creates a new user when valid input data is provided.

    Assertions
    ----------
    - HTTP response status must be 201 (Created)
    - Response must indicate success
    - The returned payload must contain the correct email
    - A user identifier must be present in the response data

    Parameters
    ----------
    client : TestClient
        FastAPI test client configured with the testing database.

    Returns
    -------
    None
    """

    # Send registration request to the authentication endpoint
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test@123"
        }
    )

    # Verify HTTP response status
    assert response.status_code == 201, "User registration failed."

    data = response.json()

    # Validate API response structure
    assert data["success"] is True
    assert data["data"]["email"] == "test@example.com"

    # Ensure the response includes the created user identifier
    assert "id" in data["data"]


def test_register_then_login(client) -> None:
    """
    Validate the end-to-end authentication flow.

    This test confirms that a user who successfully registers
    can immediately authenticate using the login endpoint and
    receive valid authentication tokens.

    Test Flow
    ---------
    1. Register a new user.
    2. Authenticate using the provided credentials.
    3. Verify that access and refresh tokens are returned.

    Parameters
    ----------
    client : TestClient
        FastAPI test client configured with the testing database.

    Returns
    -------
    None
    """

    # Step 1: Register a new user account
    reg_response = client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "Test@123"
        }
    )

    # Ensure registration was successful
    assert reg_response.status_code == 201, "Registration failed."

    # Step 2: Attempt authentication with the created account
    login_response = client.post(
        "/auth/login",
        json={
            "identifier": "login@example.com",
            "password": "Test@123"
        }
    )

    # Verify login response status
    assert login_response.status_code == 200, "Login failed."

    login_data = login_response.json()

    # Confirm API success flag
    assert login_data["success"] is True

    # Ensure authentication tokens are returned
    assert "access_token" in login_data["data"]
    assert "refresh_token" in login_data["data"]

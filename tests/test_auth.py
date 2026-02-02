def test_register_user_success(client) -> None:
    """
    Test that a new user can register successfully.

    Args:
        client: FastAPI test client fixture.

    Returns:
        None
    """
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test@123"
        }
    )

    assert response.status_code == 201, "User registration failed."

    data = response.json()

    assert data["success"] is True
    assert data["data"]["email"] == "test@example.com"
    assert "id" in data["data"]  # User ID should exist


def test_register_then_login(client) -> None:
    """
    Test registering a user and then logging in to receive access token.

    Args:
        client: FastAPI test client fixture.

    Returns:
        None
    """
    # Register user
    reg_response = client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "Test@123"
        }
    )

    assert reg_response.status_code == 201, "Registration failed."

    # Now login
    login_response = client.post(
        "/auth/login",
        json={
            "identifier": "login@example.com",
            "password": "Test@123"
        }
    )

    assert login_response.status_code == 200, "Login failed."

    login_data = login_response.json()

    assert login_data["success"] is True
    assert "access_token" in login_data["data"]
    assert "refresh_token" in login_data["data"]

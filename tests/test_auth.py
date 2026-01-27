def test_register_user(client):

    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test@123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["success"] is True
    assert data["data"]["email"] == "test@example.com"


def test_register_user(client):

    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test@123"
        }
    )

    print(response.json())

    assert response.status_code == 201


    data = response.json()

    assert data["success"] is True
    assert "access_token" in data["data"]

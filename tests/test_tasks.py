def test_create_task(client):

    login = client.post(
        "/auth/login",
        json={
            "identifier": "test@example.com",
            "password": "Test@123"
        }
    )

    assert login.status_code == 200

    token = login.json()["data"]["access_token"]

    response = client.post(
        "/tasks",   # اگر prefix فقط در main.py باشد
        json={
            "title": "Test Task",
            "description": "testing task"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["success"] is True
    assert data["data"]["title"] == "Test Task"

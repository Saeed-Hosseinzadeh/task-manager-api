def test_ci_full_flow(client):
    # 1) register
    register_response = client.post(
        "/auth/register",
        json={
            "username": "ciuser",
            "email": "ciuser@example.com",
            "password": "Test@123456"
        }
    )
    assert register_response.status_code in [200, 201]

    # 2) login
    login_response = client.post(
        "/auth/login",
        json={
            "identifier": "ciuser@example.com",
            "password": "Test@123456"
        }
    )
    assert login_response.status_code == 200

    login_data = login_response.json()
    token = login_data["data"]["access_token"]

    # 3) create task
    create_response = client.post(
        "/tasks",
        json={
            "title": "CI Task",
            "description": "Created during CI test"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code in [200, 201]
def test_db_connected(client):
    response = client.get("/health")
    assert response.status_code == 200

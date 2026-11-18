from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings


def authorization(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def tokens(client):
    response = client.post(
        "/auth/register",
        json={"username": "jwt-user", "email": "jwt@example.testdomain.org", "password": "a-test-password"},
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_access_and_refresh_token_roles(client, tokens):
    access = tokens["access_token"]
    refresh = tokens["refresh_token"]

    assert client.get("/tasks/", headers=authorization(access)).status_code == 200

    denied = client.get("/tasks/", headers=authorization(refresh))
    assert denied.status_code == 401
    assert denied.headers["www-authenticate"] == "Bearer"

    denied = client.post("/auth/refresh", json={"refresh_token": access})
    assert denied.status_code == 401
    assert denied.headers["www-authenticate"] == "Bearer"

    renewed = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert renewed.status_code == 200
    access = renewed.json()["data"]["access_token"]
    assert client.get("/tasks/", headers=authorization(access)).status_code == 200


@pytest.mark.parametrize(
    "case",
    [
        "expired",
        "wrong_signature",
        "missing_subject",
        "non_numeric_subject",
        "integer_subject",
        "out_of_range_subject",
        "missing_expiration",
        "invalid_expiration",
        "missing_type",
    ],
)
def test_invalid_token_claims_are_rejected_by_both_entry_points(client, tokens, case):
    now = datetime.now(timezone.utc)
    claims = {"sub": str(tokens["id"]), "exp": int((now + timedelta(minutes=5)).timestamp())}
    signing_key = settings.SECRET_KEY
    if case == "expired":
        claims["exp"] = int((now - timedelta(minutes=5)).timestamp())
    elif case == "wrong_signature":
        signing_key += "-different-test-key"
    elif case == "missing_subject":
        del claims["sub"]
    elif case == "non_numeric_subject":
        claims["sub"] = "invalid-user-id"
    elif case == "integer_subject":
        claims["sub"] = tokens["id"]
    elif case == "out_of_range_subject":
        claims["sub"] = "2147483648"
    elif case == "missing_expiration":
        del claims["exp"]
    elif case == "invalid_expiration":
        claims["exp"] = None

    for token_type in ("access", "refresh"):
        if case != "missing_type":
            claims["type"] = token_type
        token = jwt.encode(claims, signing_key, algorithm=settings.ALGORITHM)
        if token_type == "access":
            response = client.get("/tasks/", headers=authorization(token))
        else:
            response = client.post("/auth/refresh", json={"refresh_token": token})
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    pbkdf2_sha256__min_rounds=600_000,
    pbkdf2_sha256__default_rounds=600_000,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str | None) -> tuple[bool, str | None]:
    if hashed_password is None:
        pwd_context.dummy_verify()
        return False, None
    return pwd_context.verify_and_update(password, hashed_password)


def _create_token(data: dict[str, Any], expires_delta: timedelta, token_type: str) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(UTC) + expires_delta
    payload["type"] = token_type
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    expiration = expires_delta
    if expiration is None:
        expiration = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(data, expiration, "access")


def create_refresh_token(data: dict[str, Any]) -> str:
    return _create_token(
        data,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def decode_token_subject(token: str, *, expected_type: Literal["access", "refresh"]) -> int | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except (InvalidTokenError, TypeError, OverflowError):
        return None

    expires_at = payload["exp"]
    if type(expires_at) is not int or expires_at <= datetime.now(UTC).timestamp():
        return None
    if payload.get("type") != expected_type:
        return None

    subject = payload["sub"]
    if not isinstance(subject, str) or not (
        1 <= len(subject) <= 10 and subject.isascii() and subject.isdecimal()
    ):
        return None

    user_id = int(subject)
    # User.id is a signed PostgreSQL INTEGER.
    return user_id if 0 < user_id <= 2_147_483_647 else None

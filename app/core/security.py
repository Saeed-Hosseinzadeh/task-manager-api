from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# Password Utilities
# =========================

def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a plain password against its hashed version.
    """
    return pwd_context.verify(password, hashed)


# =========================
# Token Utilities
# =========================

def _create_token(data: Dict[str, Any], expires_delta: timedelta, token_type: str) -> str:
    """
    Internal helper function to generate JWT tokens.
    """

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({
        "exp": expire,
        "type": token_type
    })

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create an access token with a short expiration time.
    """
    return _create_token(
        data=data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access"
    )


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a refresh token with a longer expiration time.
    """
    return _create_token(
        data=data,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh"
    )


def decode_token(token: str, expected_type: str | None = None) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string.
        expected_type: Optional token type validation ("access" or "refresh").

    Raises:
        HTTPException: If token is invalid or expired.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if expected_type and payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

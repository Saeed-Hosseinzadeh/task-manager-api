from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None

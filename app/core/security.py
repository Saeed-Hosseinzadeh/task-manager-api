"""
Security Utilities

This module provides low-level security helpers used across the
authentication system. It centralizes password hashing, credential
verification, and JWT token operations.

Responsibilities
----------------
- Secure password hashing
- Password verification
- JWT access token generation
- JWT refresh token generation
- Token decoding and validation

Design Notes
------------
This module intentionally contains only stateless utility functions.
Business logic such as authentication flows or database access is
handled in the service layer.

Password Security
-----------------
Passwords are hashed using Passlib with the PBKDF2-SHA256 algorithm.
This algorithm is designed to be computationally expensive, which
helps mitigate brute-force and rainbow table attacks.

Token Strategy
--------------
Two JWT token types are used:

Access Token
    Short-lived token used for authenticating API requests.

Refresh Token
    Long-lived token used to obtain new access tokens without
    requiring the user to re-authenticate.

All tokens include:
- an expiration timestamp (`exp`)
- a token type identifier (`type`)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


# Configure Passlib password hashing context.
# PBKDF2-SHA256 provides strong password hashing suitable for
# secure credential storage.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Generate a secure hash for a plaintext password.

    This function should be used whenever a new user password needs
    to be stored. The returned hash is safe to persist in the
    database.

    Parameters
    ----------
    password : str
        Plaintext password provided by the user.

    Returns
    -------
    str
        Cryptographically hashed password.
    """
    # Hash the password using the configured Passlib context.
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored hash.

    This function compares the provided password with the stored
    hashed password and returns whether they match.

    Parameters
    ----------
    password : str
        Plaintext password supplied during authentication.

    hashed_password : str
        Stored hashed password retrieved from the database.

    Returns
    -------
    bool
        True if the password matches the stored hash, otherwise False.
    """
    # Compare plaintext password with the stored hash.
    return pwd_context.verify(password, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a signed JWT access token.

    Access tokens are used by clients to authenticate requests
    to protected API endpoints. They are intentionally short-lived.

    Parameters
    ----------
    data : Dict[str, Any]
        Payload data to embed inside the JWT (e.g., user identifier).

    expires_delta : Optional[timedelta]
        Optional custom expiration duration. If not provided,
        the default expiration defined in application settings
        will be used.

    Returns
    -------
    str
        Encoded JWT access token.
    """
    # Copy payload to avoid mutating the original input.
    to_encode = data.copy()

    # Determine token expiration time.
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Attach expiration and token type metadata.
    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    # Encode and sign the token using the configured secret key.
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a signed JWT refresh token.

    Refresh tokens are long-lived tokens that allow clients to
    obtain new access tokens without requiring the user to log in
    again.

    Parameters
    ----------
    data : Dict[str, Any]
        Payload data to embed in the refresh token.

    Returns
    -------
    str
        Encoded JWT refresh token.
    """
    # Copy payload to prevent modification of the input data.
    to_encode = data.copy()

    # Calculate refresh token expiration time.
    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    # Attach expiration and token type metadata.
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    # Encode and sign the refresh token.
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.

    The function attempts to decode the token using the configured
    secret key and algorithm. If decoding fails due to expiration,
    signature mismatch, or malformed token, the function returns None.

    Parameters
    ----------
    token : str
        Encoded JWT token string.

    Returns
    -------
    Optional[Dict[str, Any]]
        Decoded payload if the token is valid, otherwise None.
    """
    try:
        # Attempt to decode and verify the JWT token.
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload

    except JWTError:
        # Return None if the token cannot be decoded or verified.
        return None

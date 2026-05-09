"""
Authentication Service Layer

This module implements the core business logic for authentication
and user account management. It operates between the API layer
(routes/controllers) and the persistence layer (database models).

Responsibilities
----------------
- User registration
- User authentication (login)
- Access token refresh
- Password hashing and verification integration
- JWT token issuance

Design Notes
------------
This service layer isolates authentication logic from API routes,
allowing better maintainability, testing, and separation of concerns.

The module relies on:

- SQLAlchemy sessions for database interaction
- Security utilities for password hashing and token management
- Pydantic schemas for validated request data
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate, UserLogin, RefreshTokenRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def register_user(user: UserCreate, db: Session) -> dict:
    """
    Register a new user in the system.

    The function verifies that no existing account uses the same
    email address or username. If validation passes, a new user
    record is created with a securely hashed password.

    After successful registration, access and refresh tokens
    are issued for immediate authentication.

    Args:
        user (UserCreate):
            Validated registration data containing username,
            email, and plaintext password.

        db (Session):
            Active SQLAlchemy database session.

    Returns:
        dict:
            Dictionary containing user information and authentication tokens:

            - id (int): Unique identifier of the newly created user
            - username (str): User's username
            - email (str): User's email address
            - access_token (str): Generated JWT access token
            - refresh_token (str): Generated JWT refresh token
            - token_type (str): Token authentication scheme ("bearer")

    Raises:
        HTTPException:
            Raised if a user with the same email or username already exists.
    """

    # Check if a user already exists with the provided email or username.
    existing_user = (
        db.query(User)
        .filter(
            (User.email == str(user.email)) | (User.username == user.username)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )

    # Create a new user with a securely hashed password.
    new_user = User(
        username=user.username,
        email=str(user.email),
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate authentication tokens for the newly registered user.
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def login_user(user: UserLogin, db: Session) -> dict:
    """
    Authenticate a user using username or email.

    The function searches for a user whose username or email matches
    the provided identifier. If a matching user is found, the password
    is verified against the stored hashed password.

    Upon successful authentication, new access and refresh tokens
    are generated and returned.

    Args:
        user (UserLogin):
            Login payload containing an identifier (username or email)
            and a plaintext password.

        db (Session):
            Active SQLAlchemy database session.

    Returns:
        dict:
            Dictionary containing issued authentication tokens:

            - access_token (str): JWT access token
            - refresh_token (str): JWT refresh token
            - token_type (str): Token authentication scheme ("bearer")

    Raises:
        HTTPException:
            Raised if the user does not exist or the password is incorrect.
    """

    # Retrieve the user using email or username as identifier.
    db_user = (
        db.query(User)
        .filter((User.email == user.identifier) | (User.username == user.identifier))
        .first()
    )

    # Validate credentials.
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Issue new authentication tokens.
    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(data: RefreshTokenRequest) -> dict:
    """
    Generate a new access token from a refresh token.

    The provided refresh token is decoded and validated. If the
    token is valid and contains a valid subject (user identifier),
    a new access token is issued.

    This mechanism allows clients to maintain authenticated sessions
    without repeatedly requesting credentials from the user.

    Args:
        data (RefreshTokenRequest):
            Request object containing the refresh token.

    Returns:
        dict:
            Dictionary containing a newly generated access token:

            - access_token (str): Newly issued JWT access token
            - token_type (str): Token authentication scheme ("bearer")

    Raises:
        HTTPException:
            Raised if the refresh token is invalid or malformed.
    """

    # Decode and validate the refresh token.
    payload = decode_token(data.refresh_token, expected_type="refresh")
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Generate a new access token for the user.
    access_token = create_access_token(data={"sub": str(user_id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

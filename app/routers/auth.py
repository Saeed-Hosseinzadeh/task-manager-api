"""
Authentication Router

This module defines the HTTP API endpoints responsible for user
authentication and token lifecycle management.

Responsibilities
----------------
- User account registration
- User authentication (login)
- Access token renewal using a refresh token

Architecture
------------
The router represents the API layer and delegates all authentication
business logic to the authentication service layer.

Its responsibilities are intentionally limited to:

- Request validation via Pydantic schemas
- Dependency injection (database session)
- Delegation to service functions
- Returning standardized API responses

Router Prefix
-------------
The '/auth' prefix is intentionally NOT defined inside this router.

It must be applied when the router is included in the FastAPI
application instance:

    app.include_router(auth.router, prefix="/auth")

Expected Final Endpoints
------------------------
POST    /auth/register
POST    /auth/login
POST    /auth/refresh
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

# Database session dependency used for persistence operations.
from app.database import get_db

# Request schemas used for validating authentication-related payloads.
from app.schemas import UserCreate, UserLogin, RefreshTokenRequest

# Authentication service layer containing business logic.
from app.services.auth_service import (
    register_user,
    login_user,
    refresh_access_token,
)

# Utility function for returning standardized API responses.
from app.utils.response import success_response


# Router instance responsible for authentication-related endpoints.
router = APIRouter(tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    This endpoint receives validated user registration data and
    delegates the creation process to the authentication service
    layer. The service layer is responsible for:

    - Checking for duplicate users
    - Hashing the user's password
    - Persisting the user in the database
    - Issuing authentication tokens

    Parameters
    ----------
    data : UserCreate
        Validated registration payload containing user credentials
        and identifying information.

    db : Session
        SQLAlchemy database session provided via dependency injection.

    Returns
    -------
    dict
        Standardized success response containing the created user
        and issued authentication tokens.

    Raises
    ------
    HTTPException
        Raised by the service layer if the user already exists or
        if registration cannot be completed.
    """

    # Delegate registration logic to the authentication service.
    result = register_user(data, db)

    return success_response(
        data=result,
        message="User registered successfully",
    )


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and issue authentication tokens.

    This endpoint validates the provided credentials and generates
    a new pair of tokens (access token and refresh token) if the
    authentication process succeeds.

    Parameters
    ----------
    data : UserLogin
        Login payload containing the user's identifier (such as
        email or username) and password.

    db : Session
        SQLAlchemy database session used to verify user credentials.

    Returns
    -------
    dict
        Standardized success response containing the generated
        authentication tokens.

    Raises
    ------
    HTTPException
        Raised if the credentials are invalid or the user does
        not exist.
    """

    # Delegate authentication logic to the authentication service.
    result = login_user(data, db)

    return success_response(
        data=result,
        message="Login successful",
    )


@router.post("/refresh")
def refresh(data: RefreshTokenRequest):
    """
    Generate a new access token using a valid refresh token.

    This endpoint allows clients to obtain a new access token
    without requiring the user to authenticate again with their
    credentials.

    The refresh token is validated and decoded by the service
    layer before a new access token is issued.

    Parameters
    ----------
    data : RefreshTokenRequest
        Request payload containing the refresh token.

    Returns
    -------
    dict
        Standardized success response containing the newly
        generated access token.

    Raises
    ------
    HTTPException
        Raised if the refresh token is invalid, expired, or
        cannot be verified.
    """

    # Delegate token refresh logic to the authentication service.
    result = refresh_access_token(data)

    return success_response(
        data=result,
        message="Token refreshed successfully",
    )

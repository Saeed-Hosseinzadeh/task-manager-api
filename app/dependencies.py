"""
Dependencies

This module provides reusable FastAPI dependencies, including authentication
mechanisms and database session management.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from .database import get_db
from .models import User

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    """
    Dependency that extracts the current authenticated user from a JWT token.

    Args:
        token (str): The JWT token extracted from the Authorization header.
        db (Session): The SQLAlchemy database session.

    Returns:
        User: The authenticated User model object.

    Raises:
        HTTPException: If credentials are invalid, expired, or the user does not exist.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        # Decode the JWT token using the configured secret and algorithm
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Extract subject (user ID) from token payload
        user_id: str | None = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    # Retrieve user from the database
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user

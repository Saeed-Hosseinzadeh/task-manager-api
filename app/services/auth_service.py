from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import User
from app.schemas import UserCreate, UserLogin
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)


def register_user(user: UserCreate, db: Session) -> dict:
    """
    Register a new user in the system after validating email and username uniqueness.

    Steps:
    1. Check if email or username already exists
    2. Hash user password
    3. Create the user record and store in the database
    4. Generate access and refresh tokens

    Returns:
        dict: Contains access_token, refresh_token, and token_type
    """

    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()

    if existing_user:
        # More explicit error messages for better API clarity
        if existing_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token({"sub": str(new_user.id)})
    refresh_token = create_refresh_token({"sub": str(new_user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


def login_user(user: UserLogin, db: Session) -> dict:
    """
    Authenticate a user using email or username + password.

    Steps:
    1. Find user by email OR username
    2. Verify password using secure hashing
    3. Generate JWT access/refresh tokens

    Raises:
        HTTPException: If user not found or password incorrect.

    Returns:
        dict: Contains access_token, refresh_token, and token_type
    """

    identifier = user.identifier.strip()

    db_user = db.query(User).filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }

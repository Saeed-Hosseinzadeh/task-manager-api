from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token_subject,
    hash_password,
    verify_password,
)
from app.models import User
from app.schemas import RefreshTokenRequest, UserCreate, UserLogin


def register_user(user: UserCreate, db: Session) -> dict:
    existing_user = (
        db.query(User)
        .filter((User.email == str(user.email)) | (User.username == user.username))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    new_user = User(
        username=user.username,
        email=str(user.email),
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        if (
            getattr(error.orig, "pgcode", None) != "23505"
            and getattr(error.orig, "sqlite_errorname", None) != "SQLITE_CONSTRAINT_UNIQUE"
        ):
            raise
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        ) from error
    db.refresh(new_user)

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
    db_user = (
        db.query(User)
        .filter((User.email if "@" in user.identifier else User.username) == user.identifier)
        .first()
    )
    if db_user is None and "@" in user.identifier:
        db_user = db.query(User).filter(User.username == user.identifier).first()
    verified, replacement_hash = verify_password(
        user.password, db_user.hashed_password if db_user else None
    )
    if db_user is None or not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = str(db_user.id)
    if replacement_hash is not None:
        db_user.hashed_password = replacement_hash
        db.commit()

    access_token = create_access_token(data={"sub": subject})
    refresh_token = create_refresh_token(data={"sub": subject})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(data: RefreshTokenRequest, db: Session) -> dict:
    user_id = decode_token_subject(data.refresh_token, expected_type="refresh")
    if user_id is None or db.get(User, user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user_id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    LoginResponse,
    RefreshResponse,
    RefreshTokenRequest,
    RegistrationResponse,
    UserCreate,
    UserLogin,
)
from app.services.auth_service import (
    login_user,
    refresh_access_token,
    register_user,
)
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
) -> dict:
    user_data = register_user(payload, db)
    return success_response(
        data=user_data,
        message="User registered successfully",
    )


@router.post("/login", response_model=LoginResponse)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
) -> dict:
    token_data = login_user(payload, db)
    return success_response(
        data=token_data,
        message="Login successful",
    )


@router.post("/refresh", response_model=RefreshResponse)
def refresh(
    payload: RefreshTokenRequest,
) -> dict:
    token_data = refresh_access_token(payload)
    return success_response(
        data=token_data,
        message="Token refreshed successfully",
    )
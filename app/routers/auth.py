from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ErrorResponse,
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

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={
        422: {"model": ErrorResponse, "description": "Input validation failed"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Database constraint violation"},
        409: {"model": ErrorResponse, "description": "Username or email already registered"},
    },
)
def register(
    payload: UserCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    user_data = register_user(payload, db)
    response.headers["Cache-Control"] = "no-store"
    return success_response(
        data=user_data,
        message="User registered successfully",
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Database constraint violation"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
def login(
    payload: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    token_data = login_user(payload, db)
    response.headers["Cache-Control"] = "no-store"
    return success_response(
        data=token_data,
        message="Login successful",
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    responses={401: {"model": ErrorResponse, "description": "Invalid or expired refresh token"}},
)
def refresh(
    payload: RefreshTokenRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    token_data = refresh_access_token(payload, db)
    response.headers["Cache-Control"] = "no-store"
    return success_response(
        data=token_data,
        message="Token refreshed successfully",
    )

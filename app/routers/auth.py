from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.utils.response import success_response
from app.schemas import RefreshTokenRequest, UserCreate, UserLogin
from app.services.auth_service import (
    login_user,
    refresh_access_token,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    result = register_user(data, db)
    return success_response(
        data=result,
        message="User registered successfully",
    )


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    result = login_user(data, db)
    return success_response(
        data=result,
        message="Login successful",
    )


@router.post("/refresh")
def refresh(data: RefreshTokenRequest):
    result = refresh_access_token(data)
    return success_response(
        data=result,
        message="Token refreshed successfully",
    )

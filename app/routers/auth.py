from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate, UserLogin, RefreshTokenRequest
from app.services.auth_service import (
    register_user,
    login_user,
    refresh_access_token,
)
from app.utils.response import success_response

router = APIRouter(tags=["Authentication"])


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

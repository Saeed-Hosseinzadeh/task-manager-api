from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserLogin, RefreshTokenRequest, Token
# فرض می‌کنم login_user در auth_service تعریف شده باشد
from app.services.auth_service import register_user, login_user
from app.utils.response import success_response
from app.core.security import decode_token, create_access_token

# اضافه کردن تگ برای نمایش در Swagger
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(user, db)

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    # اینجا از سرویس برای احراز هویت استفاده می‌کنیم
    token_data = login_user(user_credentials, db)
    return token_data

@router.post("/refresh")
def refresh_access_token(request: RefreshTokenRequest):
    payload = decode_token(request.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    new_access_token = create_access_token(data={"sub": user_id})

    return success_response(
        data={"access_token": new_access_token, "token_type": "bearer"},
        message="Token refreshed successfully"
    )

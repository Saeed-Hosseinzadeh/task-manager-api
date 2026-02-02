from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserLogin, RefreshTokenRequest, Token, UserResponse
from app.services.auth_service import register_user, login_user
from app.core.security import decode_token, create_access_token

# Define router with tags for better Swagger documentation
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user and return access/refresh tokens.
    """
    return register_user(user, db)


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and provide access/refresh tokens.
    """
    return login_user(user_credentials, db)


@router.post("/refresh", response_model=Token)
def refresh_access_token(request: RefreshTokenRequest):
    """
    Generate a new access token using a valid refresh token.
    """
    payload = decode_token(request.refresh_token)

    # Validate payload and token type
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing user identification",
        )

    # Generate new access token
    new_access_token = create_access_token(data={"sub": str(user_id)})

    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer"
    }

from __future__ import annotations

from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

T = TypeVar("T")


# --- Base Envelope Schema ---
class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: T | None = None


# --- User & Auth Base Schemas ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Username cannot be empty")
        if " " in value:
            raise ValueError("Username must not contain spaces")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value.isdigit():
            raise ValueError("Password must not be entirely numeric")
        if " " in value:
            raise ValueError("Password must not contain spaces")
        return value


class UserLogin(BaseModel):
    identifier: str = Field(..., description="Username or email")
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# --- Task Base Schemas ---
class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_completed: bool = False
    priority: int = Field(default=1, ge=1, le=5)
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be empty")
        return value


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_completed: Optional[bool] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Title cannot be empty")
        return value


class TaskResponse(TaskBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Auth Concrete Data Payloads (Service Aligned) ---
class UserRegisterAndToken(UserResponse):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenOnly(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Task Concrete Response Wrappers ---
class TaskDetailResponse(APIResponse[TaskResponse]):
    pass


class TaskListResponse(APIResponse[list[TaskResponse]]):
    pass


class EmptyResponse(APIResponse[None]):
    pass


# --- Auth Concrete Response Wrappers ---
class RegistrationResponse(APIResponse[UserRegisterAndToken]):
    pass


class LoginResponse(APIResponse[Token]):
    pass


class RefreshResponse(APIResponse[RefreshTokenOnly]):
    pass


# --- Health Concrete Response Wrapper ---
class HealthResponse(APIResponse[dict[str, str]]):
    pass
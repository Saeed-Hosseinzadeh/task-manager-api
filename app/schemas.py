from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


# ---------------------------------------------------------
# User Schemas
# ---------------------------------------------------------

class UserBase(BaseModel):
    """Base schema for User containing shared fields."""
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user with password validation."""
    password: str = Field(..., min_length=6, max_length=50)

    @field_validator("username")
    @classmethod
    def username_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("Username must not contain spaces")
        return v

    @field_validator("password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if v.isdigit():
            raise ValueError("Password must not be entirely numeric")
        if " " in v:
            raise ValueError("Password must not contain spaces")
        return v


class UserLogin(BaseModel):
    """Schema for user authentication."""
    identifier: str = Field(..., description="Username or Email")
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    """Schema for returning user data in API responses."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------
# Token Schemas
# ---------------------------------------------------------

class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schema for requesting a new access token using a refresh token."""
    refresh_token: str


# ---------------------------------------------------------
# Task Schemas
# ---------------------------------------------------------

class TaskBase(BaseModel):
    """Base schema for Task containing shared fields."""
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_completed: bool = False


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    @field_validator("title")
    @classmethod
    def title_no_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty or only whitespace")
        return v


class TaskUpdate(BaseModel):
    """Schema for updating an existing task (all fields optional)."""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_completed: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v


class TaskResponse(TaskBase):
    """Schema for returning task details in API responses."""
    id: int
    created_at: datetime
    # Note: Ensure due_date is in the model if included here
    due_date: Optional[datetime] = None
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

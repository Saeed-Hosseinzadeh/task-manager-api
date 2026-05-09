"""
Pydantic Schemas

This module defines the Pydantic models (schemas) for request validation and
response serialization, ensuring data integrity for User, Token, and Task entities.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


# ---------------------------------------------------------
# User Schemas
# ---------------------------------------------------------

class UserBase(BaseModel):
    """
    Base schema for User containing shared identity fields.

    Attributes:
        username (str): The unique username of the user.
        email (EmailStr): The verified email address of the user.
    """
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr


class UserCreate(UserBase):
    """
    Schema for creating a new user with password validation.

    Attributes:
        password (str): Plain-text password provided during registration.
    """
    password: str = Field(..., min_length=6, max_length=50)

    @field_validator("username")
    @classmethod
    def username_no_spaces(cls, v: str) -> str:
        """Ensures the username does not contain whitespace."""
        if " " in v:
            raise ValueError("Username must not contain spaces")
        return v

    @field_validator("password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        """Validates password strength requirements."""
        if v.isdigit():
            raise ValueError("Password must not be entirely numeric")
        if " " in v:
            raise ValueError("Password must not contain spaces")
        return v


class UserLogin(BaseModel):
    """
    Schema for user authentication credentials.

    Attributes:
        identifier (str): The username or email used for login.
        password (str): The account password.
    """
    identifier: str = Field(..., description="Username or Email")
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    """
    Schema for returning user data in API responses.

    Attributes:
        id (int): The unique internal database identifier.
    """
    id: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------
# Token Schemas
# ---------------------------------------------------------

class Token(BaseModel):
    """
    Schema representing authentication tokens.

    Attributes:
        access_token (str): JWT access token for API authorization.
        refresh_token (str): JWT refresh token for renewing session access.
        token_type (str): The type of token (defaults to 'bearer').
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """
    Schema for requesting a new access token.

    Attributes:
        refresh_token (str): The current valid refresh token.
    """
    refresh_token: str


# ---------------------------------------------------------
# Task Schemas
# ---------------------------------------------------------

class TaskBase(BaseModel):
    """
    Base schema for Task containing shared fields.

    Attributes:
        title (str): The summary title of the task.
        description (Optional[str]): Extended details regarding the task.
        is_completed (bool): Current completion status.
    """
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_completed: bool = False


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    @field_validator("title")
    @classmethod
    def title_no_empty(cls, v: str) -> str:
        """Ensures the title is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or only whitespace")
        return v


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task. All fields are optional.

    Attributes:
        title (Optional[str]): Updated title of the task.
        description (Optional[str]): Updated description of the task.
        is_completed (Optional[bool]): Updated completion status.
    """
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_completed: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensures that if the title is provided, it is not blank."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v


class TaskResponse(TaskBase):
    """
    Schema for returning task details in API responses.

    Attributes:
        id (int): Unique database ID of the task.
        created_at (datetime): Timestamp of creation.
        due_date (Optional[datetime]): Optional deadline for the task.
        owner_id (int): ID of the user owning the task.
    """
    id: int
    created_at: datetime
    due_date: Optional[datetime] = None
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

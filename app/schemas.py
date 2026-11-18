from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Generic, Literal, Optional, TypeVar

from pydantic import AwareDatetime, BaseModel, BeforeValidator, ConfigDict, EmailStr, Field, field_validator

T = TypeVar("T")


# --- Base Envelope Schema ---
class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: T | None = None


class ValidationIssue(BaseModel):
    field: str
    message: str


class ErrorResponse(APIResponse[list[ValidationIssue]]):
    success: Literal[False] = False


# --- User & Auth Base Schemas ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if any(character.isspace() for character in value) or "@" in value:
            raise ValueError("Username must not contain whitespace or @")
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
    username: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


def parse_deadline(value: object) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError("A deadline must be an ISO 8601 datetime with a timezone offset") from error
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("A deadline must be an ISO 8601 datetime with a timezone offset")
    try:
        return value.astimezone(timezone.utc)
    except OverflowError as error:
        raise ValueError("The deadline is outside the representable UTC range") from error


Deadline = Annotated[AwareDatetime, BeforeValidator(parse_deadline)]


# --- Task Base Schemas ---
class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_completed: bool = False
    priority: int = Field(default=1, ge=1, le=5)
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    due_date: Deadline | None = None

    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_completed: Optional[bool] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    due_date: Deadline | None = None

    @field_validator("title", "is_completed", "priority", mode="before")
    @classmethod
    def reject_explicit_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("This field cannot be null")
        return value

    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class TaskResponse(TaskBase):
    id: int
    title: str
    priority: int
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
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


# -------------------------
# User Schemas
# -------------------------

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="نام کاربری باید بین 3 تا 30 کاراکتر باشد."
    )
    email: EmailStr = Field(..., description="ایمیل معتبر وارد کنید.")
    password: str = Field(
        ...,
        min_length=6,
        max_length=50,
        description="پسورد باید حداقل 6 کاراکتر باشد."
    )

    @field_validator("username")
    @classmethod
    def username_no_spaces(cls, v):
        if " " in v:
            raise ValueError("نام کاربری نباید شامل فاصله باشد.")
        return v

    @field_validator("password")
    @classmethod
    def password_strong(cls, v):
        if v.isdigit():
            raise ValueError("پسورد نباید فقط عدد باشد.")
        if " " in v:
            raise ValueError("پسورد نباید شامل فاصله باشد.")
        return v


class UserLogin(BaseModel):
    identifier: str = Field(..., description="ایمیل یا یوزرنیم را وارد کنید.")
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Token Schemas
# -------------------------

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# -------------------------
# Task Schemas
# -------------------------

class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="عنوان تسک باید حداقل 3 کاراکتر باشد."
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="حداکثر طول توضیحات 500 کاراکتر است."
    )
    is_completed: bool = False

    @field_validator("title")
    @classmethod
    def title_no_empty(cls, v):
        if not v.strip():
            raise ValueError("عنوان نمی‌تواند خالی باشد.")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_completed: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("عنوان نمی‌تواند خالی ارسال شود.")
        return v


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

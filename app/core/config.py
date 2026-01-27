from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # تنظیمات عمومی
    PROJECT_NAME: str = "Task Manager API"

    # تنظیمات دیتابیس
    DATABASE_URL: str

    # تنظیمات امنیتی (JWT)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # این مورد اضافه شد

    # آدرس فایل .env را مشخص می‌کنیم
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()

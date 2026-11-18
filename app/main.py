from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings

from app.routers import auth, tasks
from app.schemas import ErrorResponse, HealthResponse
from app.utils.exceptions import (
    general_exception_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from app.utils.response import success_response

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    exception_handlers={
        StarletteHTTPException: http_exception_handler,
        RequestValidationError: validation_exception_handler,
        SQLAlchemyError: sqlalchemy_exception_handler,
        Exception: general_exception_handler,
    },
)

if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

common_errors = {
    401: {"model": ErrorResponse, "description": "Authentication required"},
    422: {"model": ErrorResponse, "description": "Input validation failed"},
    500: {"model": ErrorResponse, "description": "Server error"},
}
app.include_router(auth.router, responses={
    **common_errors,
    409: {"model": ErrorResponse, "description": "Username or email already registered"},
})
app.include_router(tasks.router, responses={
    **common_errors,
    404: {"model": ErrorResponse, "description": "Task not found"},
})


@app.get("/health", tags=["Health"], response_model=HealthResponse)
def health_check() -> dict:
    return success_response(
        data={"status": "ok"},
        message="Service is healthy",
    )

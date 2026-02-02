"""
Main application entry point for the Task Manager API.

This module initializes the FastAPI application, registers global exception
handlers, and includes all application routers.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.routers import auth, tasks
from app.utils.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from app.utils.response import success_response
from app.utils.logger import logger


# ---------------------------------------------------------
# FastAPI Application Initialization
# ---------------------------------------------------------
app: FastAPI = FastAPI(
    title=settings.PROJECT_NAME,
    description="A professional Task Management API with authentication and CRUD operations.",
    version="1.0.0",
    swagger_ui_parameters={
        "docExpansion": "list",
        "persistAuthorization": True  # Keeps JWT token after page refresh
    }
)


# ---------------------------------------------------------
# Application Startup Event
# ---------------------------------------------------------
@app.on_event("startup")
async def startup_event() -> None:
    """
    Executes when the application starts.

    Used for logging system startup or initializing services.
    """
    logger.info("Task Manager API started successfully")


# ---------------------------------------------------------
# Exception Handlers Registration
# ---------------------------------------------------------
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# ---------------------------------------------------------
# Routers Registration
# ---------------------------------------------------------
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])


# ---------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------
@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint used to verify API availability.

    Returns:
        dict: Standard API response containing project metadata.
    """
    return success_response(
        data={
            "project": settings.PROJECT_NAME,
            "status": "online",
            "docs": "/docs"
        },
        message="API is running"
    )

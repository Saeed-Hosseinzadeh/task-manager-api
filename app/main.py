from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
# فقط ایمپورت از مسیر صحیح (routers)
from app.routers import auth, tasks
from app.utils.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)

app = FastAPI(
    title="Task Manager API",
    description="A professional Task Management API built with FastAPI.",
    version="1.0.0",
    swagger_ui_parameters={
        "docExpansion": "list",
        "persistAuthorization": True
    }
)

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])


@app.get("/", tags=["Root"])
def root():
    return {
        "success": True,
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "status": "online",
        "docs": "/docs"
    }

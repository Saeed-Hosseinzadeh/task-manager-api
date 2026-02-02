"""
Global Exception Handlers for FastAPI.
Standardizes error responses and logs issues across the application.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from .response import error_response
from .logger import logger


async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle Starlette/FastAPI HTTP exceptions.

    Args:
        _request: The incoming HTTP request (unused).
        exc: The exception instance containing detail and status code.

    Returns:
        JSONResponse: Standardized error format with specific status code.
    """
    logger.warning(f"HTTP error: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=str(exc.detail))  # Fixed: removed status_code
    )


async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors (422 Unprocessable Entity).

    Args:
        _request: The incoming HTTP request (unused).
        exc: The validation error details.

    Returns:
        JSONResponse: Standardized error format with list of validation issues.
    """
    # Extract field name and message from Pydantic errors
    cleaned_errors = [
        {"field": " -> ".join(map(str, err["loc"][1:])), "message": err["msg"]}
        for err in exc.errors()
    ]

    logger.warning(f"Validation error: {cleaned_errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            message="Input validation failed",
            data=cleaned_errors
        )
    )


async def sqlalchemy_exception_handler(_request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle SQLAlchemy database related errors.

    Args:
        _request: The incoming HTTP request (unused).
        exc: The database exception.

    Returns:
        JSONResponse: 500 Internal Server Error with a safe message.
    """
    logger.error(f"Database error: {str(exc)}")  # Log the full error for debugging

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(message="A database error occurred")
    )


async def general_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for any unexpected server errors.

    Args:
        _request: The incoming HTTP request (unused).
        exc: The unhandled exception.

    Returns:
        JSONResponse: 500 Internal Server Error with a generic message.
    """
    logger.error(f"Unexpected system error: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(message="An unexpected server error occurred")
    )

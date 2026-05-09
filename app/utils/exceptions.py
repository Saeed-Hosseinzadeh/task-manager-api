"""
Global Exception Handlers

This module defines centralized exception handlers for the FastAPI application.
The handlers standardize API error responses and ensure that all errors are
properly logged for monitoring and debugging purposes.
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
    Handle HTTP exceptions raised by FastAPI or Starlette.

    This handler captures all HTTP-related errors and converts them into
    a standardized API response format.

    Args:
        _request (Request): The incoming HTTP request (unused but required by FastAPI).
        exc (StarletteHTTPException): The raised HTTP exception instance.

    Returns:
        JSONResponse: A structured JSON response containing the error message
        and the corresponding HTTP status code.
    """
    logger.warning(f"HTTP error: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=str(exc.detail))
    )


async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle request validation errors raised by Pydantic.

    These errors occur when incoming request data fails schema validation.
    The handler extracts field-level validation messages and returns them
    in a consistent response structure.

    Args:
        _request (Request): The incoming HTTP request (unused but required by FastAPI).
        exc (RequestValidationError): The validation exception raised by FastAPI.

    Returns:
        JSONResponse: A standardized response containing validation error details.
    """
    # Extract field name and validation message from Pydantic error structure
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
    Handle SQLAlchemy database exceptions.

    This captures database-related errors and prevents internal database
    details from being exposed to API clients while logging the full error
    internally for debugging.

    Args:
        _request (Request): The incoming HTTP request (unused).
        exc (SQLAlchemyError): The raised SQLAlchemy exception.

    Returns:
        JSONResponse: A 500 Internal Server Error response with a safe message.
    """
    logger.error(f"Database error: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(message="A database error occurred")
    )


async def general_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for unexpected application errors.

    This serves as a fallback mechanism for any unhandled exceptions,
    ensuring the API always returns a consistent error format.

    Args:
        _request (Request): The incoming HTTP request (unused).
        exc (Exception): The unhandled exception instance.

    Returns:
        JSONResponse: A 500 Internal Server Error response with a generic message.
    """
    logger.error(f"Unexpected system error: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(message="An unexpected server error occurred")
    )

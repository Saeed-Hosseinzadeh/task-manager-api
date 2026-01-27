from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from .response import error_response
from .logger import logger


# ----------------------------
# Handle HTTP Exceptions
# ----------------------------
async def http_exception_handler(_request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP error: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=str(exc.detail),
            status_code=exc.status_code
        )
    )


# ----------------------------
# Handle Validation Errors
# ----------------------------
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")

    cleaned_errors = []

    for err in exc.errors():
        err_copy = err.copy()
        ctx = err_copy.get("ctx")

        if ctx:
            cleaned_ctx = {}
            for key, value in ctx.items():
                if isinstance(value, Exception):
                    cleaned_ctx[key] = str(value)
                else:
                    cleaned_ctx[key] = value
            err_copy["ctx"] = cleaned_ctx

        cleaned_errors.append(err_copy)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            message="Invalid input data",
            data=cleaned_errors,
            status_code=422
        )
    )


# ----------------------------
# Handle Database Errors
# ----------------------------
async def sqlalchemy_exception_handler(_request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            message="Database error occurred",
            status_code=500
        )
    )


# ----------------------------
# Handle Unexpected Server Errors (500)
# ----------------------------
async def general_exception_handler(_request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            message="Internal server error",
            status_code=500
        )
    )

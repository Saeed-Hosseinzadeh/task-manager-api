from __future__ import annotations

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.logger import logger
from app.utils.response import error_response


def _request_path(request: Request) -> str:
    return f"{request.method} {request.url.path}"


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    logger.warning("HTTP %s on %s: %s", exc.status_code, _request_path(request), exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=str(exc.detail)),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = [
        {
            "field": ".".join(str(part) for part in error["loc"][1:]) or "body",
            "message": error["msg"],
        }
        for error in exc.errors()
    ]

    logger.warning("Validation error on %s: %s", _request_path(request), errors)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            message="Input validation failed",
            data=errors,
        ),
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    if isinstance(exc, IntegrityError):
        logger.warning("Database integrity error on %s: %s", _request_path(request), exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response(message="The request could not be completed"),
        )

    logger.exception("Database error on %s", _request_path(request))

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(message="A database error occurred"),
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception("Unhandled error on %s", _request_path(request))

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(message="An unexpected server error occurred"),
    )

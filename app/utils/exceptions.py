from __future__ import annotations

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.response import error_response

logger = logging.getLogger("uvicorn.error")


def _request_path(request: Request) -> str:
    route = request.scope.get("route")
    return f"{request.method} {getattr(route, 'path', '<unmatched>')}"


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    logger.warning("HTTP %s on %s", exc.status_code, _request_path(request))

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=str(exc.detail)),
        headers=exc.headers,
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

    logger.warning("Input validation failed on %s", _request_path(request))

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
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
        logger.warning("Database integrity error on %s", _request_path(request))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response(message="The request could not be completed"),
        )

    logger.error("Database error %s on %s", type(exc).__name__, _request_path(request))

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(message="A database error occurred"),
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error("Unhandled error %s on %s", type(exc).__name__, _request_path(request))

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(message="An unexpected server error occurred"),
    )

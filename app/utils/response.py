# app/utils/response.py

from fastapi import Response, status
from typing import Any, Optional


def success_response(
    data: Any = None,
    message: Optional[str] = None,
    status_code: int = status.HTTP_200_OK
):
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    data: Any = None
):
    return {
        "success": False,
        "message": message,
        "data": data
    }

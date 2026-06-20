from __future__ import annotations

from typing import Any


def success_response(data: Any = None, message: str | None = None) -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str, data: Any = None) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "data": data,
    }

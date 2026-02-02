from typing import Any, Optional


def success_response(
    data: Any = None,
    message: Optional[str] = None
) -> dict:
    """
    Standard successful API response format.
    """

    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(
    message: str,
    data: Any = None
) -> dict:
    """
    Standard error API response format.
    """

    return {
        "success": False,
        "message": message,
        "data": data
    }

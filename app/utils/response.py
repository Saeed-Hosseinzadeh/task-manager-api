"""
API Response Utilities

This module provides standardized helper functions for formatting API responses.
Using a consistent response structure improves maintainability, readability,
and client-side integration across the application.
"""

from typing import Any, Optional


def success_response(
    data: Any = None,
    message: Optional[str] = None
) -> dict:
    """
    Generate a standardized successful API response.

    Args:
        data (Any, optional): The payload returned from the API endpoint.
        message (Optional[str], optional): A human-readable success message.

    Returns:
        dict: A dictionary representing a successful API response structure.
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
    Generate a standardized error API response.

    Args:
        message (str): A description of the error that occurred.
        data (Any, optional): Additional contextual information related to the error.

    Returns:
        dict: A dictionary representing an error response structure.
    """

    return {
        "success": False,
        "message": message,
        "data": data
    }

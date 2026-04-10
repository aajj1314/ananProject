"""Standard API response helpers."""

from typing import Any

from app.utils.errors import ErrorCode


def success_response(data: Any, message: str | None = None) -> dict[str, Any]:
    """Return the normalized success payload."""

    return {
        "code": ErrorCode.SUCCESS.code,
        "message": message or ErrorCode.SUCCESS.message,
        "data": data,
    }

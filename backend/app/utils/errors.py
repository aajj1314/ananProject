"""Standardized error codes and API exceptions."""

from dataclasses import dataclass

from fastapi import HTTPException, status


@dataclass(frozen=True)
class ErrorMeta:
    """Error payload metadata."""

    code: int
    message: str


class ErrorCode:
    """Unified application error codes."""

    SUCCESS = ErrorMeta(code=0, message="操作成功")
    UNAUTHORIZED = ErrorMeta(code=40101, message="未授权")
    TOKEN_EXPIRED = ErrorMeta(code=40102, message="令牌已过期")
    INVALID_TOKEN = ErrorMeta(code=40103, message="无效的令牌")
    INVALID_PARAMS = ErrorMeta(code=40001, message="参数错误")
    MISSING_PARAMS = ErrorMeta(code=40002, message="缺少必要参数")
    DEVICE_ALREADY_BOUND = ErrorMeta(code=40003, message="设备已绑定")
    DEVICE_NOT_FOUND = ErrorMeta(code=40401, message="设备未找到")
    INTERNAL_SERVER_ERROR = ErrorMeta(code=50001, message="服务器内部错误")


class AppException(HTTPException):
    """HTTP exception carrying the standard business payload."""

    def __init__(self, error: ErrorMeta, http_status: int, detail: str | None = None) -> None:
        payload = {
            "code": error.code,
            "message": error.message,
            "detail": detail,
        }
        super().__init__(status_code=http_status, detail=payload)


def unauthorized(detail: str | None = None) -> AppException:
    """Build an unauthorized exception."""

    return AppException(ErrorCode.UNAUTHORIZED, status.HTTP_401_UNAUTHORIZED, detail)


def invalid_params(detail: str | None = None) -> AppException:
    """Build an invalid parameter exception."""

    return AppException(ErrorCode.INVALID_PARAMS, status.HTTP_400_BAD_REQUEST, detail)


def not_found(detail: str | None = None) -> AppException:
    """Build a not-found exception."""

    return AppException(ErrorCode.DEVICE_NOT_FOUND, status.HTTP_404_NOT_FOUND, detail)


def conflict(detail: str | None = None) -> AppException:
    """Build a conflict exception."""

    return AppException(ErrorCode.DEVICE_ALREADY_BOUND, status.HTTP_409_CONFLICT, detail)

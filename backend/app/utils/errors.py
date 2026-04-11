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
    BAD_REQUEST = ErrorMeta(code=40000, message="请求错误")
    INVALID_PARAMS = ErrorMeta(code=40001, message="参数错误")
    MISSING_PARAMS = ErrorMeta(code=40002, message="缺少必要参数")
    DEVICE_ALREADY_BOUND = ErrorMeta(code=40003, message="设备已绑定")
    PHONE_ALREADY_REGISTERED = ErrorMeta(code=40004, message="手机号已注册")
    UNAUTHORIZED = ErrorMeta(code=40101, message="未授权")
    TOKEN_EXPIRED = ErrorMeta(code=40102, message="令牌已过期")
    INVALID_TOKEN = ErrorMeta(code=40103, message="无效的令牌")
    FORBIDDEN = ErrorMeta(code=40301, message="禁止访问")
    DEVICE_NOT_FOUND = ErrorMeta(code=40401, message="设备未找到")
    USER_NOT_FOUND = ErrorMeta(code=40402, message="用户未找到")
    FENCE_NOT_FOUND = ErrorMeta(code=40403, message="围栏未找到")
    LOCATION_NOT_FOUND = ErrorMeta(code=40404, message="位置记录未找到")
    NOT_FOUND = ErrorMeta(code=40400, message="资源未找到")
    ALARM_NOT_FOUND = ErrorMeta(code=40405, message="报警记录未找到")
    RATE_LIMITED = ErrorMeta(code=42901, message="请求过于频繁")
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


def bad_request(detail: str | None = None) -> AppException:
    """Build a bad request exception."""

    return AppException(ErrorCode.BAD_REQUEST, status.HTTP_400_BAD_REQUEST, detail)


def unauthorized(detail: str | None = None) -> AppException:
    """Build an unauthorized exception."""

    return AppException(ErrorCode.UNAUTHORIZED, status.HTTP_401_UNAUTHORIZED, detail)


def invalid_params(detail: str | None = None) -> AppException:
    """Build an invalid parameter exception."""

    return AppException(ErrorCode.INVALID_PARAMS, status.HTTP_400_BAD_REQUEST, detail)


def forbidden(detail: str | None = None) -> AppException:
    """Build a forbidden exception."""

    return AppException(ErrorCode.FORBIDDEN, status.HTTP_403_FORBIDDEN, detail)


def not_found(detail: str | None = None) -> AppException:
    """Build a generic not-found exception."""

    return AppException(ErrorCode.NOT_FOUND, status.HTTP_404_NOT_FOUND, detail)


def device_not_found(detail: str | None = None) -> AppException:
    """Build a device-not-found exception."""

    return AppException(ErrorCode.DEVICE_NOT_FOUND, status.HTTP_404_NOT_FOUND, detail)


def user_not_found(detail: str | None = None) -> AppException:
    """Build a user-not-found exception."""

    return AppException(ErrorCode.USER_NOT_FOUND, status.HTTP_404_NOT_FOUND, detail)


def fence_not_found(detail: str | None = None) -> AppException:
    """Build a fence-not-found exception."""

    return AppException(ErrorCode.FENCE_NOT_FOUND, status.HTTP_404_NOT_FOUND, detail)


def location_not_found(detail: str | None = None) -> AppException:
    """Build a location-not-found exception."""

    return AppException(ErrorCode.LOCATION_NOT_FOUND, status.HTTP_404_NOT_FOUND, detail)


def alarm_not_found(detail: str | None = None) -> AppException:
    """Build an alarm-not-found exception."""

    return AppException(ErrorCode.ALARM_NOT_FOUND, status.HTTP_404_NOT_FOUND, detail)


def conflict(detail: str | None = None) -> AppException:
    """Build a conflict exception."""

    return AppException(ErrorCode.DEVICE_ALREADY_BOUND, status.HTTP_409_CONFLICT, detail)


def phone_already_registered(detail: str | None = None) -> AppException:
    """Build a phone-already-registered exception."""

    return AppException(ErrorCode.PHONE_ALREADY_REGISTERED, status.HTTP_409_CONFLICT, detail)

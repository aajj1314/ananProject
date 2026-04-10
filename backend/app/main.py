"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.alarm import router as alarm_router
from app.api.v1.auth import router as auth_router
from app.api.v1.device import router as device_router
from app.api.v1.fence import router as fence_router
from app.api.v1.location import router as location_router
from app.config import get_settings
from app.models import alarm, device, fence, location, user  # noqa: F401
from app.models.base import Base
from app.utils.cache import close_redis_client
from app.utils.database import engine
from app.utils.errors import ErrorCode
from app.utils.rate_limit import RateLimitMiddleware


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create schema on startup for the initial scaffold."""

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await close_redis_client()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.add_middleware(RateLimitMiddleware)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(device_router, prefix=settings.api_v1_prefix)
app.include_router(fence_router, prefix=settings.api_v1_prefix)
app.include_router(location_router, prefix=settings.api_v1_prefix)
app.include_router(alarm_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check() -> dict:
    """Simple health endpoint."""

    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Normalize validation errors."""

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": ErrorCode.INVALID_PARAMS.code,
            "message": ErrorCode.INVALID_PARAMS.message,
            "detail": exc.errors(),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(_: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Normalize database errors."""

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": ErrorCode.INTERNAL_SERVER_ERROR.code,
            "message": ErrorCode.INTERNAL_SERVER_ERROR.message,
            "detail": str(exc),
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Normalize unexpected errors."""

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": ErrorCode.INTERNAL_SERVER_ERROR.code,
            "message": ErrorCode.INTERNAL_SERVER_ERROR.message,
            "detail": str(exc),
        },
    )

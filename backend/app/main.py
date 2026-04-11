"""FastAPI application entrypoint."""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.alarm import router as alarm_router
from app.api.v1.auth import router as auth_router
from app.api.v1.device import router as device_router
from app.api.v1.fence import router as fence_router
from app.api.v1.health import router as health_router
from app.api.v1.location import router as location_router
from app.api.v1.admin import router as admin_router
from app.config import get_settings
from app.models import alarm, device, fence, location, user  # noqa: F401
from app.models.base import Base
from app.utils.cache import close_redis_client
from app.utils.database import engine
from app.utils.errors import ErrorCode
from app.utils.metrics import get_metrics_registry
from app.utils.rate_limit import RateLimitMiddleware


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create schema on startup for the initial scaffold."""

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    
    # Create default admin user if not exists
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.models.user import User
    from app.utils.security import hash_password
    
    async with AsyncSession(engine) as session:
        try:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.phone == "15577305913"))
            existing_user = result.scalar_one_or_none()
            if existing_user is None:
                admin_user = User(
                    phone="15577305913",
                    password=hash_password("passwor"),
                    nickname="管理员",
                    role="admin"
                )
                session.add(admin_user)
                await session.commit()
                print("Default admin user created successfully")
        except Exception as e:
            print(f"Error creating default admin user: {e}")
            await session.rollback()
    
    yield
    await close_redis_client()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.add_middleware(RateLimitMiddleware)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(device_router, prefix=settings.api_v1_prefix)
app.include_router(fence_router, prefix=settings.api_v1_prefix)
app.include_router(location_router, prefix=settings.api_v1_prefix)
app.include_router(alarm_router, prefix=settings.api_v1_prefix)
app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(admin_router, prefix=settings.api_v1_prefix)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collect request metrics."""
    registry = get_metrics_registry()
    path = request.url.path
    method = request.method

    # Skip metrics for health and static paths
    if path.startswith("/health") or path.startswith("/api/v1/health"):
        return await call_next(request)

    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000

    # Record metrics
    registry.counter("http_requests_total", "Total HTTP requests").add(
        1, {"method": method, "path": path, "status": str(response.status_code)}
    )
    registry.histogram("http_request_duration_ms", "HTTP request duration").add(
        duration_ms, {"method": method, "path": path}
    )
    registry.counter(f"http_requests_{method.lower()}", f"{method} requests").add(1)

    return response


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

"""FastAPI application entrypoint."""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

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
from app.utils.errors import AppException, ErrorCode
from app.utils.metrics import get_metrics_registry
from app.utils.rate_limit import RateLimitMiddleware
from app.utils.response import success_response


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create schema on startup for the initial scaffold."""

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

        # Auto-migration: add missing columns to existing tables
        from sqlalchemy import inspect, text

        def _migrate_missing_columns(sync_conn):
            """Check each table for missing columns and add them via ALTER TABLE."""
            inspector = inspect(sync_conn)
            for table_name, table_obj in Base.metadata.tables.items():
                existing_columns = {col["name"] for col in inspector.get_columns(table_name)}
                for column in table_obj.columns:
                    if column.name not in existing_columns:
                        col_type = column.type.compile(dialect=sync_conn.dialect)
                        nullable = "" if column.nullable else " NOT NULL"
                        default_clause = ""
                        if column.server_default is not None:
                            default_clause = f" DEFAULT {column.server_default.arg}"
                        elif column.default is not None:
                            default_val = column.default.arg
                            if callable(default_val):
                                # For func.now() style defaults, use CURRENT_TIMESTAMP
                                default_clause = " DEFAULT CURRENT_TIMESTAMP"
                            elif isinstance(default_val, str):
                                # Sanitize default value to prevent SQL injection
                                escaped_val = default_val.replace("'", "''")
                                default_clause = f" DEFAULT '{escaped_val}'"
                            else:
                                default_clause = f" DEFAULT {default_val}"
                        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type}{nullable}{default_clause}"
                        print(f"Auto-migration: {alter_sql}")
                        sync_conn.execute(text(alter_sql))

        await connection.run_sync(_migrate_missing_columns)

    # Create default admin user if not exists
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.models.user import User
    from app.utils.security import hash_password

    admin_phone = settings.admin_phone
    admin_password = settings.admin_password

    if admin_phone and admin_password:
        async with AsyncSession(engine) as session:
            try:
                from sqlalchemy import select
                result = await session.execute(select(User).where(User.phone == admin_phone))
                existing_user = result.scalar_one_or_none()
                if existing_user is None:
                    admin_user = User(
                        phone=admin_phone,
                        password=hash_password(admin_password),
                        nickname="管理员",
                        role="admin"
                    )
                    session.add(admin_user)
                    await session.commit()
                    print("Default admin user created successfully")
                elif existing_user.role != "admin":
                    existing_user.role = "admin"
                    await session.commit()
                    print("Default admin user role updated to admin")
            except Exception as e:
                print(f"Error creating default admin user: {e}")
                await session.rollback()

    yield
    await close_redis_client()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

# CORS middleware - allow frontend cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    return success_response({"status": "ok"})


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    """Normalize business logic exceptions."""

    payload = exc.detail or {}
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": payload.get("code", ErrorCode.INTERNAL_SERVER_ERROR.code),
            "message": payload.get("message", ErrorCode.INTERNAL_SERVER_ERROR.message),
            "data": None,
            "detail": payload.get("detail"),
        },
    )


@app.exception_handler(StarletteHTTPException)
async def starlette_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Normalize Starlette/FastAPI HTTP exceptions (e.g. 404 Not Found)."""

    error_map = {
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        405: ErrorCode.BAD_REQUEST,
    }
    error = error_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": error.code,
            "message": error.message,
            "data": None,
            "detail": exc.detail if exc.detail != error.message else None,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Normalize validation errors."""

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": ErrorCode.INVALID_PARAMS.code,
            "message": ErrorCode.INVALID_PARAMS.message,
            "data": None,
            "detail": exc.errors(),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(_: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Normalize database errors - do not expose internal details."""

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": ErrorCode.INTERNAL_SERVER_ERROR.code,
            "message": ErrorCode.INTERNAL_SERVER_ERROR.message,
            "data": None,
            "detail": None,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Normalize unexpected errors - do not expose internal details."""

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": ErrorCode.INTERNAL_SERVER_ERROR.code,
            "message": ErrorCode.INTERNAL_SERVER_ERROR.message,
            "data": None,
            "detail": None,
        },
    )

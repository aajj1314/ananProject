"""Health check and operational metrics endpoints."""

import asyncio
import time
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User
from app.utils.database import get_db_session
from app.utils.metrics import get_metrics_registry
from app.utils.response import success_response
from app.utils.security import get_admin_user

router = APIRouter(prefix="/health", tags=["health"])
settings = get_settings()
startup_time = datetime.now(timezone.utc)


@router.get("")
async def health_check() -> dict:
    """Basic health endpoint with application info."""
    uptime = (datetime.now(timezone.utc) - startup_time).total_seconds()
    return success_response(
        {
            "status": "ok",
            "uptime_seconds": uptime,
        }
    )


@router.get("/detailed")
async def detailed_health(session: AsyncSession = Depends(get_db_session)) -> dict:
    """Detailed health check with database and connectivity."""
    uptime = (datetime.now(timezone.utc) - startup_time).total_seconds()

    # Database health
    db_ok = False
    db_latency_ms = 0.0
    try:
        start = time.perf_counter()
        await session.execute(text("SELECT 1"))
        db_latency_ms = (time.perf_counter() - start) * 1000
        db_ok = True
    except Exception:
        pass

    # Redis health (optional)
    redis_ok = None
    try:
        from app.utils.cache import get_redis_client

        redis = await get_redis_client()
        if redis:
            start = time.perf_counter()
            await redis.ping()
            redis_ok = True
    except Exception:
        redis_ok = False

    overall_status = "ok" if db_ok else "degraded"

    return success_response(
        {
            "status": overall_status,
            "app": settings.app_name,
            "env": settings.app_env,
            "uptime_seconds": uptime,
            "started_at": startup_time.isoformat(),
            "checks": {
                "database": {
                    "status": "ok" if db_ok else "error",
                    "latency_ms": round(db_latency_ms, 2),
                },
                "redis": {
                    "status": "ok" if redis_ok else "error" if redis_ok is False else "skipped",
                },
            },
        }
    )


@router.get("/metrics")
async def get_metrics(window_seconds: float = 60.0) -> dict:
    """Get operational metrics for the application."""
    registry = get_metrics_registry()
    metrics = registry.get_all_summaries(window_seconds)

    # Add process-level metrics
    uptime = (datetime.now(timezone.utc) - startup_time).total_seconds()

    return success_response(
        {
            "window_seconds": window_seconds,
            "uptime_seconds": uptime,
            "metrics": metrics,
        }
    )


@router.post("/metrics/reset")
async def reset_metrics(
    _current_user: Annotated[User, Depends(get_admin_user)],
) -> dict:
    """Reset all metrics (admin only, for testing/debug)."""

    registry = get_metrics_registry()
    registry.reset()
    return success_response(None, message="指标已重置")

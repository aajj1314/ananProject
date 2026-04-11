"""Simple request rate-limiting middleware."""

import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.utils.errors import ErrorCode


settings = get_settings()
_request_buckets: dict[str, deque[float]] = defaultdict(deque)

# Maximum number of tracked clients to prevent memory exhaustion
_MAX_TRACKED_CLIENTS = 10000
# Cleanup interval (seconds) to remove stale entries
_CLEANUP_INTERVAL = 300
_last_cleanup = time.time()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-client sliding-window limiter."""

    async def dispatch(self, request: Request, call_next):
        """Reject requests that exceed the configured window."""

        global _last_cleanup

        # Use the direct client IP, not X-Forwarded-For which can be spoofed
        # If behind a reverse proxy, configure trusted proxies separately
        client_host = request.client.host if request.client else "anonymous"
        now = time.time()
        bucket = _request_buckets[client_host]
        while bucket and now - bucket[0] > settings.rate_limit_window_seconds:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "code": ErrorCode.RATE_LIMITED.code,
                    "message": ErrorCode.RATE_LIMITED.message,
                    "data": None,
                    "detail": "Too many requests, please try again later",
                },
            )
        bucket.append(now)

        # Periodic cleanup of stale entries to prevent memory leaks
        if now - _last_cleanup > _CLEANUP_INTERVAL:
            _last_cleanup = now
            stale_keys = [
                key for key, dq in _request_buckets.items()
                if not dq or now - dq[-1] > settings.rate_limit_window_seconds
            ]
            for key in stale_keys:
                del _request_buckets[key]

        # Prevent unbounded memory growth
        if len(_request_buckets) > _MAX_TRACKED_CLIENTS:
            # Remove oldest entries
            oldest_keys = sorted(
                _request_buckets.keys(),
                key=lambda k: _request_buckets[k][-1] if _request_buckets[k] else 0,
            )[: len(_request_buckets) - _MAX_TRACKED_CLIENTS]
            for key in oldest_keys:
                del _request_buckets[key]

        return await call_next(request)

"""Simple request rate-limiting middleware."""

import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings


settings = get_settings()
_request_buckets: dict[str, deque[float]] = defaultdict(deque)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-client sliding-window limiter."""

    async def dispatch(self, request: Request, call_next):
        """Reject requests that exceed the configured window."""

        client_host = request.client.host if request.client else "anonymous"
        now = time.time()
        bucket = _request_buckets[client_host]
        while bucket and now - bucket[0] > settings.rate_limit_window_seconds:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "code": 42901,
                    "message": "请求过于频繁",
                    "detail": f"Allowed {settings.rate_limit_requests} requests per window",
                },
            )
        bucket.append(now)
        return await call_next(request)

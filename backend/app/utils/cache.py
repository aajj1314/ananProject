"""Redis-backed cache helpers with in-memory fallback."""

import json
import time
from collections.abc import AsyncGenerator

from redis import asyncio as redis

from app.config import get_settings


settings = get_settings()

# In-memory cache stores (value, expire_at) tuples for TTL support
_memory_cache: dict[str, tuple[str, float]] = {}
_redis_client: redis.Redis | None = None


async def get_redis_client() -> redis.Redis | None:
    """Return a lazily created Redis client when available."""

    global _redis_client

    if _redis_client is not None:
        return _redis_client
    try:
        _redis_client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        await _redis_client.ping()
        return _redis_client
    except Exception:
        _redis_client = None
        return None


def _cleanup_expired_memory_cache() -> None:
    """Remove expired entries from the in-memory cache to prevent memory leaks."""
    now = time.monotonic()
    expired_keys = [k for k, (_, expire_at) in _memory_cache.items() if expire_at > 0 and now > expire_at]
    for key in expired_keys:
        del _memory_cache[key]


async def cache_get(key: str) -> dict | list | None:
    """Read JSON data from cache."""

    client = await get_redis_client()
    if client is not None:
        raw_value = await client.get(key)
    else:
        # Periodically clean up expired entries from memory cache
        _cleanup_expired_memory_cache()
        entry = _memory_cache.get(key)
        if entry is not None:
            raw_value, expire_at = entry
            if expire_at > 0 and time.monotonic() > expire_at:
                del _memory_cache[key]
                raw_value = None
            else:
                raw_value = raw_value
        else:
            raw_value = None
    if not raw_value:
        return None
    return json.loads(raw_value)


async def cache_set(key: str, value: dict | list, ttl_seconds: int | None = None) -> None:
    """Store JSON data in cache."""

    payload = json.dumps(value, default=str)
    client = await get_redis_client()
    ttl = ttl_seconds or settings.cache_ttl_seconds
    if client is not None:
        await client.set(key, payload, ex=ttl)
        return
    # Store with expiration timestamp for in-memory fallback
    expire_at = time.monotonic() + ttl if ttl > 0 else 0
    _memory_cache[key] = (payload, expire_at)


async def cache_delete(key: str) -> None:
    """Delete a cache entry."""

    client = await get_redis_client()
    if client is not None:
        await client.delete(key)
        return
    _memory_cache.pop(key, None)


async def close_redis_client() -> None:
    """Close the active Redis client if one exists."""

    global _redis_client

    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None

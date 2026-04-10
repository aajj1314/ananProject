"""Redis-backed cache helpers with in-memory fallback."""

import json
from collections.abc import AsyncGenerator

from redis import asyncio as redis

from app.config import get_settings


settings = get_settings()
_memory_cache: dict[str, str] = {}
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


async def cache_get(key: str) -> dict | list | None:
    """Read JSON data from cache."""

    client = await get_redis_client()
    if client is not None:
        raw_value = await client.get(key)
    else:
        raw_value = _memory_cache.get(key)
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
    _memory_cache[key] = payload


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

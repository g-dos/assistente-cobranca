from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis, from_url

from assistente_cobranca.core.config import settings


_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    return _redis


async def cache_get_json(key: str) -> dict[str, Any] | None:
    r = get_redis()
    raw = await r.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


async def cache_set_json(key: str, value: dict[str, Any], ttl_s: int) -> None:
    r = get_redis()
    await r.set(key, json.dumps(value), ex=ttl_s)


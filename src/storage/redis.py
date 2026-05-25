import json
import logging
from redis.asyncio import Redis
from src.config import settings

logger = logging.getLogger(__name__)

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


async def cache_window(device_id: str, sensor_id: str,
                       data_points: list[dict], ttl: int = 3600) -> None:
    key = f"window:{device_id}:{sensor_id}"
    await redis_client.set(key, json.dumps(data_points, default=str), ex=ttl)


async def get_cached_window(device_id: str, sensor_id: str) -> list[dict]:
    key = f"window:{device_id}:{sensor_id}"
    raw = await redis_client.get(key)
    if raw:
        return json.loads(raw)
    return []


async def set_device_state(device_id: str, state: str) -> None:
    await redis_client.hset("device_states", device_id, state)


async def get_device_state(device_id: str) -> str | None:
    return await redis_client.hget("device_states", device_id)


async def check_rate_limit(key: str, window_seconds: int,
                           max_count: int) -> bool:
    current = await redis_client.incr(f"ratelimit:{key}")
    if current == 1:
        await redis_client.expire(f"ratelimit:{key}", window_seconds)
    return current <= max_count

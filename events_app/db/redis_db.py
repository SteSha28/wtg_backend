import redis.asyncio as redis
from redis.asyncio.client import Redis

from events_app.core.config import settings


async def get_redis_connection():
    return redis.Redis(
        host=settings.REDIS_JWT_HOST,
        port=settings.REDIS_JWT_PORT,
        decode_responses=True,
    )


async def store_token(
        redis: Redis,
        token: str,
        user_id: int,
        ttl: int = settings.ACCESS_TOKEN_EXPIRE,
):
    await redis.set(token, user_id, ex=ttl)


async def check_token(
        redis: Redis,
        token: str,
) -> int | None:
    user_id = await redis.get(token)
    return int(user_id) if user_id else None


async def delete_token(
        redis: Redis,
        token: str,
):
    await redis.delete(token)

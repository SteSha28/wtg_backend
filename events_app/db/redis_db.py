import redis.asyncio as redis
from redis.asyncio.client import Redis

from events_app.core.config import settings


async def get_redis_connection():
    """Создаёт и возвращает асинхронное подключение к Redis."""
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
    """
    Сохраняет токен в Redis с заданным TTL.

    Args:
        - redis: Подключение к Redis.
        - token: JWT токен.
        - user_id: Идентификатор пользователя.
        - ttl: Время жизни токена в секундах.
    """
    await redis.set(token, user_id, ex=ttl)


async def check_token(
        redis: Redis,
        token: str,
) -> int | None:
    """
    Проверяет токен в Redis и возвращает user_id, если найден.

    Args:
        - redis: Подключение к Redis.
        - token: JWT токен.

    Returns:
        - user_id или None, если токен не найден.
    """
    user_id = await redis.get(token)
    return int(user_id) if user_id else None


async def delete_token(
        redis: Redis,
        token: str,
):
    """Удаляет токен из Redis."""
    await redis.delete(token)

import redis.asyncio as redis
from backend.Core.config import settings

pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=20,
    decode_responses=True
)


def get_redis_client():
    return redis.Redis(connection_pool=pool)
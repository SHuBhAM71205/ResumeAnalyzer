import redis.asyncio as redis
from Core.config import settings

# Initialize an async connection pool for high-performance
pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=20,
    decode_responses=True
)

def get_redis():
    """Get a Redis client instance using the pool."""
    return redis.Redis(connection_pool=pool)
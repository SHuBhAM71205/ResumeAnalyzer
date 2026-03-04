from fastapi import Request,HTTPException
import redis.asyncio as redis
from Core.config import settings

redis = redis.from_url(f"redis://{settings.REDIS_HOST}",decode_respose=True)


async def rate_limit_middleware(request: Request, call_next):
    user_ip = request.client.host
    # Increment key for the IP, set 60s expiry
    requests = await redis.incr(user_ip)
    if requests == 1:
        await redis.expire(user_ip, 60)
    if requests > 10:  # Limit: 10 requests per minute
        raise HTTPException(status_code=429, detail="Too many vibes, slow down!")
    return await call_next(request)
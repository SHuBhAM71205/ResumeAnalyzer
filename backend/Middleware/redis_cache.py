from redis.asyncio import Redis
from backend.Core.reddis import get_redis_client
from fastapi.requests import Request

async def reddis_cache_middleware(request: Request, call_next):
        
    client = get_redis_client()

    client.set("key","value",ex=60)
    print(client.get("key"))
    
 
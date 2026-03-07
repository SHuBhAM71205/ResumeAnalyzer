from fastapi import Request
from fastapi.responses import JSONResponse

from backend.Core.config import settings
from backend.Core.reddis import get_redis_client


async def global_rate_limit_middleware(request: Request, call_next):
    
    user_key = f"global_rate_limit:{request.client.host}"
    
    client = get_redis_client()
    
    try:
    
        request_count = await client.incr(user_key)
        
        if request_count == 1:
            await client.expire(user_key, 60)
            
        if request_count > settings.GLOBAL_RATE_LIMIT_PER_MINUTE:
            
            return JSONResponse(
                status_code=429,
                content={
                    "err":"Too many Request Chill/"
                }
            )
            
    except Exception as e:
        
        print(f"Redis Error: {e}")
    
    response = await call_next(request)
    return response


async def auth_rate_limit_middleware(request: Request, call_next):
    # Placeholder for future auth-specific rate limiting logic
    
    client = get_redis_client()
    
    user_key = f"auth_rate_limit:{request.client.host}"
    
    try:
        
        counts = await client.incr(user_key)
        
        if counts==1:
            client.expire(user_key,60,nx=True)
            
        if counts > settings.AUTH_RATE_LIMIT_PER_MINUTE:
            
            return JSONResponse(
                    status_code=429,
                    content={
                        "err":"Too many Request Chill/"
                    }
                )
    
    
    except Exception as e:
        print(f"Redis Error: {e}")
    
    response = await call_next(request)
    return response
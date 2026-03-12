from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from backend.Core.config import settings
from backend.Core.reddis import get_redis_client


async def global_rate_limit_middleware(request: Request, call_next):
    
    host = request.client.host if request.client else "unknown"
    user_key = f"global_rate_limit:{host}"
    
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
    
    host = request.client.host if request.client else "unknown"
    client = get_redis_client()
    
    user_key = f"auth_rate_limit:{host}"
    
    try:
        
        counts = await client.incr(user_key)
        
        if counts==1:
            await client.expire(user_key,60,nx=True)
            
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


async def auth_rate_limiter(request: Request):
    host = request.client.host if request.client else "unknown"
    client = get_redis_client()
    user_key = f"auth_rate_limit:{host}"
    try:
        counts = await client.incr(user_key)
        if counts == 1:
            await client.expire(user_key, 60)
        if counts > settings.AUTH_RATE_LIMIT_PER_MINUTE:
            raise HTTPException(status_code=429, detail="Too many auth requests. Please try again later.")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Redis Error: {e}")

async def resume_rate_limmiter_middleware(request: Request, call_next):
    
    # Placeholder for future resume-specific rate limiting logic
    
    host = request.client.host if request.client else "unknown"
    client = get_redis_client()
    
    user_key = f"resume_rate_limit:{host}" # potential bug that people may use proxy to make it out to be different user, in future we can use user_id instead of ip for better accuracy
    
    try:
        counts = await client.incr(user_key)
        
        if counts == 1:
            await client.expire(user_key, 60)
        
        if counts > settings.RESUME_UPLOAD_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"err": "Too many requests. Please try again later."}
            )

    except Exception as e:
        print(f"Redis Error: {e}")

    response = await call_next(request)
    return response

async def resume_rate_limiter(request: Request):
    host = request.client.host if request.client else "unknown"
    client = get_redis_client()
    user_key = f"resume_rate_limit:{host}"
    try:
        counts = await client.incr(user_key)
        if counts == 1:
            await client.expire(user_key, 60)
        if counts > settings.RESUME_UPLOAD_LIMIT:
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    except Exception as e:
        print(f"Redis Error: {e}")

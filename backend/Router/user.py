from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.Core.db import get_db
from backend.Model.model import User
from backend.Service.auth import get_current_user
from backend.Model.auth_model import UserResponse
from backend.Middleware.redis_cache import redis_profile_cache_get, redis_profile_cache_set


router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.get("/", response_model=UserResponse)
async def user_root(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.get("/{id}", response_model=UserResponse)
async def get_profile(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user profile by ID with Redis caching.
    
    Returns cached profile if available, otherwise fetches from database.
    """
    if id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only access your own profile")

    # Try to get from cache first
    cached_profile = await redis_profile_cache_get(id)
    if cached_profile:
        return UserResponse.model_validate(cached_profile)

    # Cache miss - fetch from database
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert to dict and cache
    user_dict = UserResponse.model_validate(user).model_dump(mode="json")
    await redis_profile_cache_set(id, user_dict)

    return UserResponse.model_validate(user)

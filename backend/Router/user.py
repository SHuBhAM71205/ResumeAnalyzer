from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.Core.db import get_db
from backend.Model.model import User
from backend.Service.auth import get_current_user
from backend.Model.auth_model import UserResponse

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.get("/", response_model=UserResponse)
async def user_root(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.get("/{id}", response_model=UserResponse)
async def get_profile(id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)



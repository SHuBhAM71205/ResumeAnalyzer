from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession  # Changed this
from sqlalchemy import select
from datetime import timedelta

from backend.Core.db import get_db
from backend.Model.model import User
from backend.Service.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from backend.Model.auth_model import (
    LoginRequest, 
    SignupRequest, 
    UserResponse, 
    LoginResponse
)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user) # Use model_validate for Pydantic v2
    )

@router.post("/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: AsyncSession = Depends(get_db)):
    # Corrected Async Query
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    new_user = User(
        email=request.email,
        name=request.name,
        hashed_password=get_password_hash(request.password),
        is_active=True,
        is_oauth_used=False
    )
    
    db.add(new_user)
    await db.commit()   # Must await commit
    await db.refresh(new_user) # Must await refresh
    
    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

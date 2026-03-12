from datetime import datetime, timedelta, timezone
from jwt import encode, decode
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from typing import Optional
from backend.Core.config import settings

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.Core.db import get_db
from backend.Model.model import User

security = HTTPBearer(auto_error=False)


SECRET_KEY = settings.SECRETE_KEY
ALGORITHM = settings.HASH_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


pswd_hash = PasswordHash.recommended()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str
    exp: Optional[datetime] = None


def verify_password(plain_password, hash_password):
    return pswd_hash.verify(plain_password, hash_password)


def get_password_hash(plain_password):
    
    return pswd_hash.hash(plain_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str):
    """Verify JWT token and return the token data if valid, otherwise return None"""
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject: str = payload.get("sub")
        expires_at = payload.get("exp")
        
        if subject is None:
            return None
        
        token_data = TokenData(sub=subject, exp=expires_at)
        return token_data
    
    except InvalidTokenError:
        return None


async def get_user_by_subject(subject: str, db: AsyncSession) -> Optional[User]:
    try:
        from uuid import UUID
        user_uuid = UUID(subject)
    except ValueError:
        return None

    result = await db.execute(select(User).where(User.id == user_uuid))
    return result.scalars().first()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    request_user = getattr(request.state, "current_user", None)
    if request_user is not None:
        if not request_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return request_user

    if credentials is None:
        raise credentials_exception

    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception

    user = await get_user_by_subject(token_data.sub, db)
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user


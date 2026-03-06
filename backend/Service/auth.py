from datetime import datetime, timedelta
from jwt import encode, decode
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from typing import Optional
from backend.Core.config import settings

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.Core.db import get_db
from backend.Model.model import User

security = HTTPBearer()


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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str):
    """Verify JWT token and return the token data if valid, otherwise return None"""
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject: str = payload.get("sub")
        
        if subject is None:
            return None
        
        token_data = TokenData(sub=subject)
        return token_data
    
    except InvalidTokenError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception
    
    # Needs a UUID context. Token subject is stringified UUID.
    try:
        from uuid import UUID
        user_uuid = UUID(token_data.sub)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user


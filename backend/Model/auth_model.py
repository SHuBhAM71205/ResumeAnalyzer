from pydantic import BaseModel, EmailStr
from uuid import UUID

#Request/Response Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    is_active: bool
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

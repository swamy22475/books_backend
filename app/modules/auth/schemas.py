from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ==================== SCHOOL SCHEMAS ====================

class SchoolBase(BaseModel):
    name: str
    admin_email: str
    admin_name: Optional[str] = None

class SchoolCreate(SchoolBase):
    pass

class School(SchoolBase):
    id: int
    tenant_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    school_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    school_name: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    tenant_id: str
    is_admin: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(User):
    pass

# ==================== TOKEN SCHEMAS ====================

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User
    tenant_id: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    tenant_id: Optional[str] = None
    username: Optional[str] = None

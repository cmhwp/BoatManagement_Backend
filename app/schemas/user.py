from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from app.models.enums import UserRole, UserStatus


class UserBase(BaseModel):
    """用户基础模式"""
    username: str
    email: EmailStr
    phone: Optional[str] = None
    real_name: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模式"""
    password: str
    role: UserRole = UserRole.USER

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度不能少于6位')
        return v

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('用户名长度不能少于3位')
        return v


class UserUpdate(BaseModel):
    """用户更新模式"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    role: UserRole
    status: UserStatus
    is_verified: bool
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模式"""
    username: str  # 可以是用户名、邮箱或手机号
    password: str


class Token(BaseModel):
    """Token响应模式"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Token数据模式"""
    user_id: Optional[int] = None
    username: Optional[str] = None 
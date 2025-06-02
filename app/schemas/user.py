from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: EmailStr
    phone: Optional[str] = None
    real_name: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[datetime] = None
    address: Optional[str] = None
    region_id: Optional[int] = None


class UserCreate(UserBase):
    """用户创建模型"""
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 20:
            raise ValueError('用户名长度必须在3-20位之间')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少为6位')
        return v


class UserUpdate(BaseModel):
    """用户更新模型"""
    real_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[datetime] = None
    address: Optional[str] = None
    region_id: Optional[int] = None
    avatar: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    phone: Optional[str] = None
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[datetime] = None
    address: Optional[str] = None
    region_id: Optional[int] = None
    role: UserRole
    status: UserStatus
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """密码修改模型"""
    old_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('新密码长度至少为6位')
        return v


class RoleApplicationCreate(BaseModel):
    """角色申请创建模型"""
    target_role: UserRole
    application_reason: str
    supporting_documents: Optional[List[str]] = None


class RoleApplicationResponse(BaseModel):
    """角色申请响应模型"""
    id: int
    user_id: int
    target_role: UserRole
    application_reason: str
    supporting_documents: Optional[str] = None
    status: str
    reviewer_id: Optional[int] = None
    review_comment: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse 
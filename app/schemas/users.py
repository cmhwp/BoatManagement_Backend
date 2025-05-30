from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.users import UserRole


class UserBase(BaseModel):
    username: str
    phone: str
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.user


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: int
    create_at: datetime
    last_login: Optional[datetime] = None
    update_at: datetime
    is_delete: bool


class RoleApplicationCreate(BaseModel):
    target_role: str
    application_data: dict


class RoleApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    application_id: int
    user_id: int
    target_role: str
    application_data: dict
    status: str
    applied_time: datetime
    reviewed_time: Optional[datetime] = None
    review_notes: Optional[str] = None 
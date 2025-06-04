from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class CrewBase(BaseModel):
    """船员基础模式"""
    id_card_no: str
    license_no: Optional[str] = None
    license_type: Optional[str] = None
    license_expiry: Optional[datetime] = None
    years_of_experience: int = 0
    specialties: Optional[str] = None  # JSON字符串
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None


class CrewCreate(CrewBase):
    """船员创建模式"""
    user_id: int
    
    @field_validator('id_card_no')
    @classmethod
    def validate_id_card_no(cls, v):
        if len(v) != 18:
            raise ValueError('身份证号必须为18位')
        return v
    
    @field_validator('years_of_experience')
    @classmethod
    def validate_years_of_experience(cls, v):
        if v < 0:
            raise ValueError('从业年限不能为负数')
        return v


class CrewUpdate(BaseModel):
    """船员更新模式"""
    license_no: Optional[str] = None
    license_type: Optional[str] = None
    license_expiry: Optional[datetime] = None
    years_of_experience: Optional[int] = None
    specialties: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    is_available: Optional[bool] = None
    current_status: Optional[str] = None


class CrewResponse(CrewBase):
    """船员响应模式"""
    id: int
    user_id: int
    is_available: bool
    current_status: str
    rating: float
    total_services: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CrewListResponse(BaseModel):
    """船员列表响应模式"""
    id: int
    user_id: int
    license_no: Optional[str] = None
    license_type: Optional[str] = None
    years_of_experience: int
    is_available: bool
    current_status: str
    rating: float
    total_services: int
    
    class Config:
        from_attributes = True


class CrewStatusUpdate(BaseModel):
    """船员状态更新模式"""
    is_available: bool
    current_status: str 
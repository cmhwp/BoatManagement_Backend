from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.enums import BoatType, BoatStatus


class BoatBase(BaseModel):
    """船艇基础模式"""
    name: str
    boat_type: BoatType
    registration_no: str
    license_no: Optional[str] = None
    length: Optional[Decimal] = None
    width: Optional[Decimal] = None
    passenger_capacity: Optional[int] = None
    engine_power: Optional[str] = None
    current_location: Optional[str] = None
    safety_equipment: Optional[str] = None
    insurance_no: Optional[str] = None
    insurance_expiry: Optional[datetime] = None
    daily_rate: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    description: Optional[str] = None
    images: Optional[str] = None


class BoatCreate(BoatBase):
    """船艇创建模式"""
    merchant_id: int
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError('船艇名称不能少于2个字符')
        return v
    
    @validator('registration_no')
    def validate_registration_no(cls, v):
        if len(v) < 5:
            raise ValueError('注册编号格式不正确')
        return v


class BoatUpdate(BaseModel):
    """船艇更新模式"""
    name: Optional[str] = None
    boat_type: Optional[BoatType] = None
    license_no: Optional[str] = None
    length: Optional[Decimal] = None
    width: Optional[Decimal] = None
    passenger_capacity: Optional[int] = None
    engine_power: Optional[str] = None
    current_location: Optional[str] = None
    safety_equipment: Optional[str] = None
    insurance_no: Optional[str] = None
    insurance_expiry: Optional[datetime] = None
    daily_rate: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    description: Optional[str] = None
    images: Optional[str] = None
    status: Optional[BoatStatus] = None
    is_available: Optional[bool] = None


class BoatResponse(BoatBase):
    """船艇响应模式"""
    id: int
    merchant_id: int
    status: BoatStatus
    is_available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BoatListResponse(BaseModel):
    """船艇列表响应模式"""
    id: int
    name: str
    boat_type: BoatType
    registration_no: str
    passenger_capacity: Optional[int] = None
    status: BoatStatus
    is_available: bool
    daily_rate: Optional[Decimal] = None
    current_location: Optional[str] = None
    
    class Config:
        from_attributes = True


class BoatStatusUpdate(BaseModel):
    """船艇状态更新模式"""
    status: BoatStatus
    is_available: bool
    current_location: Optional[str] = None 
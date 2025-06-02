from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.boat import BoatStatus, BoatType


class BoatBase(BaseModel):
    """船艇基础模型"""
    name: str
    registration_number: Optional[str] = None
    boat_type: BoatType
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    length: Optional[Decimal] = None
    width: Optional[Decimal] = None
    max_capacity: Optional[int] = None
    max_speed: Optional[Decimal] = None
    fuel_type: Optional[str] = None
    amenities: Optional[List[str]] = None
    safety_equipment: Optional[List[str]] = None
    license_number: Optional[str] = None
    license_expire_date: Optional[datetime] = None
    insurance_number: Optional[str] = None
    insurance_expire_date: Optional[datetime] = None
    hourly_rate: Optional[Decimal] = None
    daily_rate: Optional[Decimal] = None
    home_port: Optional[str] = None
    current_location: Optional[str] = None
    gps_coordinates: Optional[str] = None
    
    @field_validator('max_capacity')
    @classmethod
    def validate_capacity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('载客量必须大于0')
        return v
    
    @field_validator('hourly_rate', 'daily_rate')
    @classmethod
    def validate_rates(cls, v):
        if v is not None and v < 0:
            raise ValueError('价格不能为负数')
        return v


class BoatCreate(BoatBase):
    """船艇创建模型"""
    name: str
    boat_type: BoatType


class BoatUpdate(BaseModel):
    """船艇更新模型"""
    name: Optional[str] = None
    boat_type: Optional[BoatType] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    length: Optional[Decimal] = None
    width: Optional[Decimal] = None
    max_capacity: Optional[int] = None
    max_speed: Optional[Decimal] = None
    fuel_type: Optional[str] = None
    amenities: Optional[List[str]] = None
    safety_equipment: Optional[List[str]] = None
    license_number: Optional[str] = None
    license_expire_date: Optional[datetime] = None
    insurance_number: Optional[str] = None
    insurance_expire_date: Optional[datetime] = None
    hourly_rate: Optional[Decimal] = None
    daily_rate: Optional[Decimal] = None
    home_port: Optional[str] = None
    current_location: Optional[str] = None
    gps_coordinates: Optional[str] = None
    status: Optional[BoatStatus] = None
    is_green_certified: Optional[bool] = None
    
    @field_validator('max_capacity')
    @classmethod
    def validate_capacity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('载客量必须大于0')
        return v
    
    @field_validator('hourly_rate', 'daily_rate')
    @classmethod
    def validate_rates(cls, v):
        if v is not None and v < 0:
            raise ValueError('价格不能为负数')
        return v


class BoatResponse(BaseModel):
    """船艇响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    merchant_id: int
    name: str
    registration_number: Optional[str] = None
    boat_type: BoatType
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    length: Optional[Decimal] = None
    width: Optional[Decimal] = None
    max_capacity: Optional[int] = None
    max_speed: Optional[Decimal] = None
    fuel_type: Optional[str] = None
    amenities: Optional[str] = None  # JSON string
    safety_equipment: Optional[str] = None  # JSON string
    images: Optional[str] = None  # JSON string
    license_number: Optional[str] = None
    license_expire_date: Optional[datetime] = None
    insurance_number: Optional[str] = None
    insurance_expire_date: Optional[datetime] = None
    status: BoatStatus
    is_green_certified: bool
    hourly_rate: Optional[Decimal] = None
    daily_rate: Optional[Decimal] = None
    home_port: Optional[str] = None
    current_location: Optional[str] = None
    gps_coordinates: Optional[str] = None
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    maintenance_notes: Optional[str] = None
    purchase_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class BoatListResponse(BaseModel):
    """船艇列表响应模型"""
    id: int
    name: str
    boat_type: BoatType
    status: BoatStatus
    max_capacity: Optional[int] = None
    hourly_rate: Optional[Decimal] = None
    daily_rate: Optional[Decimal] = None
    is_green_certified: bool
    images: Optional[str] = None
    created_at: datetime


class BoatStatusUpdate(BaseModel):
    """船艇状态更新模型"""
    status: BoatStatus
    notes: Optional[str] = None


class BoatMaintenanceUpdate(BaseModel):
    """船艇维护信息更新模型"""
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    maintenance_notes: Optional[str] = None


class BoatImageUpload(BaseModel):
    """船艇图片上传响应模型"""
    image_url: str
    thumbnail_url: Optional[str] = None 
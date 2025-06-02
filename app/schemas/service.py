from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.service import ServiceStatus, ServiceType


class ServiceBase(BaseModel):
    """服务基础模型"""
    title: str
    description: Optional[str] = None
    service_type: ServiceType
    price: Decimal
    original_price: Optional[Decimal] = None
    price_unit: str = "person"
    duration: Optional[int] = None
    max_participants: Optional[int] = None
    min_participants: int = 1
    age_requirement: Optional[str] = None
    includes: Optional[List[str]] = None
    excludes: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    schedule_type: str = "fixed"
    advance_booking_hours: int = 24
    meeting_point: Optional[str] = None
    route_description: Optional[str] = None
    
    @field_validator('price', 'original_price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('价格必须大于0')
        return v
    
    @field_validator('max_participants', 'min_participants')
    @classmethod
    def validate_participants(cls, v):
        if v is not None and v <= 0:
            raise ValueError('参与人数必须大于0')
        return v
    
    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError('服务时长必须大于0')
        return v


class ServiceCreate(ServiceBase):
    """服务创建模型"""
    title: str
    service_type: ServiceType
    price: Decimal
    boat_id: Optional[int] = None
    region_id: Optional[int] = None
    available_times: Optional[List[str]] = None


class ServiceUpdate(BaseModel):
    """服务更新模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    service_type: Optional[ServiceType] = None
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    price_unit: Optional[str] = None
    duration: Optional[int] = None
    max_participants: Optional[int] = None
    min_participants: Optional[int] = None
    age_requirement: Optional[str] = None
    includes: Optional[List[str]] = None
    excludes: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    schedule_type: Optional[str] = None
    available_times: Optional[List[str]] = None
    advance_booking_hours: Optional[int] = None
    meeting_point: Optional[str] = None
    route_description: Optional[str] = None
    status: Optional[ServiceStatus] = None
    is_featured: Optional[bool] = None
    is_green_service: Optional[bool] = None
    boat_id: Optional[int] = None
    region_id: Optional[int] = None
    
    @field_validator('price', 'original_price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('价格必须大于0')
        return v
    
    @field_validator('max_participants', 'min_participants')
    @classmethod
    def validate_participants(cls, v):
        if v is not None and v <= 0:
            raise ValueError('参与人数必须大于0')
        return v


class ServiceResponse(BaseModel):
    """服务响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    merchant_id: int
    boat_id: Optional[int] = None
    region_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    service_type: ServiceType
    price: Decimal
    original_price: Optional[Decimal] = None
    price_unit: str
    duration: Optional[int] = None
    max_participants: Optional[int] = None
    min_participants: int
    age_requirement: Optional[str] = None
    includes: Optional[str] = None  # JSON string
    excludes: Optional[str] = None  # JSON string
    requirements: Optional[str] = None  # JSON string
    schedule_type: str
    available_times: Optional[str] = None  # JSON string
    advance_booking_hours: int
    meeting_point: Optional[str] = None
    route_description: Optional[str] = None
    images: Optional[str] = None  # JSON string
    videos: Optional[str] = None  # JSON string
    status: ServiceStatus
    is_featured: bool
    is_green_service: bool
    rating: Optional[Decimal] = None
    review_count: int
    booking_count: int
    created_at: datetime
    updated_at: datetime


class ServiceListResponse(BaseModel):
    """服务列表响应模型"""
    id: int
    title: str
    service_type: ServiceType
    price: Decimal
    original_price: Optional[Decimal] = None
    duration: Optional[int] = None
    max_participants: Optional[int] = None
    status: ServiceStatus
    is_featured: bool
    is_green_service: bool
    rating: Optional[Decimal] = None
    review_count: int
    images: Optional[str] = None
    meeting_point: Optional[str] = None
    created_at: datetime


class ServiceStatusUpdate(BaseModel):
    """服务状态更新模型"""
    status: ServiceStatus
    notes: Optional[str] = None


class ServiceScheduleUpdate(BaseModel):
    """服务排期更新模型"""
    available_times: List[str]
    advance_booking_hours: Optional[int] = None


class ServiceImageUpload(BaseModel):
    """服务图片上传响应模型"""
    image_url: str
    thumbnail_url: Optional[str] = None


class ServiceSearchFilter(BaseModel):
    """服务搜索筛选模型"""
    service_type: Optional[ServiceType] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    max_participants: Optional[int] = None
    is_green_service: Optional[bool] = None
    region_id: Optional[int] = None
    keyword: Optional[str] = None
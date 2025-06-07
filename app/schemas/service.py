from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal

from app.models.enums import ServiceStatus, ServiceType


class ServiceBase(BaseModel):
    """服务基础模式"""
    name: str = Field(..., description="服务名称")
    service_type: ServiceType = Field(..., description="服务类型")
    description: Optional[str] = Field(None, description="服务描述")
    base_price: Decimal = Field(..., description="基础价格")
    duration: Optional[int] = Field(None, description="服务时长(分钟)")
    max_participants: Optional[int] = Field(None, description="最大参与人数")
    min_participants: Optional[int] = Field(1, description="最小参与人数")
    location: Optional[str] = Field(None, description="服务地点")
    requirements: Optional[str] = Field(None, description="服务要求")
    included_items: Optional[str] = Field(None, description="包含项目")
    excluded_items: Optional[str] = Field(None, description="不包含项目")
    safety_instructions: Optional[str] = Field(None, description="安全须知")
    cancellation_policy: Optional[str] = Field(None, description="取消政策")
    images: Optional[str] = Field(None, description="服务图片URL")


class ServiceCreate(ServiceBase):
    """创建服务模式"""
    pass


class ServiceUpdate(BaseModel):
    """更新服务模式"""
    name: Optional[str] = Field(None, description="服务名称")
    service_type: Optional[ServiceType] = Field(None, description="服务类型")
    description: Optional[str] = Field(None, description="服务描述")
    base_price: Optional[Decimal] = Field(None, description="基础价格")
    duration: Optional[int] = Field(None, description="服务时长(分钟)")
    max_participants: Optional[int] = Field(None, description="最大参与人数")
    min_participants: Optional[int] = Field(None, description="最小参与人数")
    location: Optional[str] = Field(None, description="服务地点")
    requirements: Optional[str] = Field(None, description="服务要求")
    included_items: Optional[str] = Field(None, description="包含项目")
    excluded_items: Optional[str] = Field(None, description="不包含项目")
    safety_instructions: Optional[str] = Field(None, description="安全须知")
    cancellation_policy: Optional[str] = Field(None, description="取消政策")
    images: Optional[str] = Field(None, description="服务图片URL")
    status: Optional[ServiceStatus] = Field(None, description="服务状态")


class ServiceResponse(BaseModel):
    """服务响应模式"""
    id: int
    name: str
    service_type: ServiceType
    description: Optional[str] = None
    base_price: Decimal
    duration: Optional[int] = None
    max_participants: Optional[int] = None
    min_participants: int
    location: Optional[str] = None
    requirements: Optional[str] = None
    included_items: Optional[str] = None
    excluded_items: Optional[str] = None
    safety_instructions: Optional[str] = None
    cancellation_policy: Optional[str] = None
    images: Optional[str] = None
    merchant_id: int
    status: ServiceStatus
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    merchant_name: Optional[str] = None
    total_orders: Optional[int] = 0
    average_rating: Optional[Decimal] = None

    class Config:
        from_attributes = True


class ServiceListResponse(BaseModel):
    """服务列表响应模式"""
    id: int
    name: str
    service_type: ServiceType
    base_price: Decimal
    duration: Optional[int] = None
    max_participants: Optional[int] = None
    location: Optional[str] = None
    merchant_id: int
    merchant_name: Optional[str] = None
    status: ServiceStatus
    total_orders: Optional[int] = 0
    average_rating: Optional[Decimal] = None
    images: Optional[str] = None

    class Config:
        from_attributes = True 
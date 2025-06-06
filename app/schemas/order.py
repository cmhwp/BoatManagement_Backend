from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal

from app.models.enums import OrderStatus, OrderType


class OrderBase(BaseModel):
    """订单基础模式"""
    order_type: OrderType = Field(..., description="订单类型")
    service_id: Optional[int] = Field(None, description="服务ID")
    product_id: Optional[int] = Field(None, description="农产品ID")
    quantity: int = Field(1, description="数量")
    participants: Optional[int] = Field(None, description="参与人数")
    scheduled_at: datetime = Field(..., description="预约服务时间")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    special_requirements: Optional[str] = Field(None, description="特殊需求")
    notes: Optional[str] = Field(None, description="备注")
    coupon_id: Optional[int] = Field(None, description="使用的优惠券ID")


class OrderCreate(OrderBase):
    """创建订单模式"""
    pass


class OrderUpdate(BaseModel):
    """更新订单模式"""
    status: Optional[OrderStatus] = Field(None, description="订单状态")
    special_requirements: Optional[str] = Field(None, description="特殊需求")
    notes: Optional[str] = Field(None, description="备注")


class OrderAssignCrew(BaseModel):
    """派单模式"""
    crew_id: int = Field(..., description="指派的船员ID")
    boat_id: Optional[int] = Field(None, description="指定的船艇ID")
    notes: Optional[str] = Field(None, description="派单备注")


class OrderStatusUpdate(BaseModel):
    """订单状态更新模式"""
    status: OrderStatus = Field(..., description="新状态")
    notes: Optional[str] = Field(None, description="状态变更备注")


class UserInfo(BaseModel):
    """用户信息模式"""
    id: int
    username: str
    real_name: Optional[str] = None
    phone: Optional[str] = None


class MerchantInfo(BaseModel):
    """商家信息模式"""
    id: int
    business_name: str
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None


class ServiceInfo(BaseModel):
    """服务信息模式"""
    id: int
    name: str
    service_type: str
    base_price: Decimal
    duration: Optional[int] = None
    max_participants: Optional[int] = None


class CrewInfo(BaseModel):
    """船员信息模式"""
    id: int
    user_id: int
    license_no: Optional[str] = None
    license_type: Optional[str] = None
    rating: Optional[Decimal] = None
    is_available: bool


class BoatInfo(BaseModel):
    """船艇信息模式"""
    id: int
    name: str
    boat_type: str
    capacity: Optional[int] = None
    status: str


class OrderResponse(BaseModel):
    """订单响应模式"""
    id: int
    order_no: str
    user_id: int
    merchant_id: int
    order_type: OrderType
    status: OrderStatus
    service_id: Optional[int] = None
    product_id: Optional[int] = None
    boat_id: Optional[int] = None
    crew_id: Optional[int] = None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    discount_amount: Decimal
    total_price: Decimal
    scheduled_at: datetime
    service_date: Optional[datetime] = None
    service_time: Optional[str] = None
    duration: Optional[int] = None
    participants: Optional[int] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    special_requirements: Optional[str] = None
    notes: Optional[str] = None
    coupon_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # 关联信息
    user: Optional[UserInfo] = None
    merchant: Optional[MerchantInfo] = None
    service: Optional[ServiceInfo] = None
    crew: Optional[CrewInfo] = None
    boat: Optional[BoatInfo] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """订单列表响应模式"""
    id: int
    order_no: str
    order_type: OrderType
    status: OrderStatus
    service_name: Optional[str] = None
    total_price: Decimal
    scheduled_at: datetime
    created_at: datetime
    user_name: Optional[str] = None
    merchant_name: Optional[str] = None
    crew_name: Optional[str] = None

    class Config:
        from_attributes = True


class OrderStats(BaseModel):
    """订单统计模式"""
    total_orders: int = Field(0, description="总订单数")
    pending_orders: int = Field(0, description="待付款订单数")
    paid_orders: int = Field(0, description="已付款订单数")
    pending_assignment_orders: int = Field(0, description="待派单订单数")
    confirmed_orders: int = Field(0, description="已确认订单数")
    in_progress_orders: int = Field(0, description="进行中订单数")
    completed_orders: int = Field(0, description="已完成订单数")
    cancelled_orders: int = Field(0, description="已取消订单数")
    total_revenue: Decimal = Field(Decimal('0.00'), description="总营收")
    today_orders: int = Field(0, description="今日订单数")
    today_revenue: Decimal = Field(Decimal('0.00'), description="今日营收") 
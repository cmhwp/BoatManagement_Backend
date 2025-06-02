from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.models.order import OrderStatus, OrderType, RefundStatus


class ParticipantDetail(BaseModel):
    """参与者详情模型"""
    name: str
    phone: str
    id_card: Optional[str] = None
    age: Optional[int] = None
    notes: Optional[str] = None


class OrderBase(BaseModel):
    """订单基础模型"""
    order_type: OrderType
    service_id: Optional[int] = None
    product_ids: Optional[List[int]] = None
    bundle_id: Optional[int] = None
    participant_count: Optional[int] = None
    participant_details: Optional[List[ParticipantDetail]] = None
    booking_date: Optional[datetime] = None
    booking_time: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_phone: Optional[str] = None
    delivery_contact: Optional[str] = None
    delivery_notes: Optional[str] = None
    customer_notes: Optional[str] = None
    coupon_code: Optional[str] = None
    
    @field_validator('participant_count')
    @classmethod
    def validate_participant_count(cls, v):
        if v is not None and v <= 0:
            raise ValueError('参与人数必须大于0')
        return v


class OrderCreate(OrderBase):
    """订单创建模型"""
    order_type: OrderType
    
    @field_validator('service_id', 'product_ids', 'bundle_id')
    @classmethod
    def validate_order_content(cls, v, info):
        # 根据订单类型验证必需字段
        order_type = info.data.get('order_type')
        field_name = info.field_name
        
        if order_type == OrderType.SERVICE and field_name == 'service_id':
            if not v:
                raise ValueError('服务订单必须指定服务ID')
        elif order_type == OrderType.PRODUCT and field_name == 'product_ids':
            if not v or len(v) == 0:
                raise ValueError('产品订单必须指定至少一个产品ID')
        elif order_type == OrderType.BUNDLE and field_name == 'bundle_id':
            if not v:
                raise ValueError('套餐订单必须指定套餐ID')
        
        return v


class OrderUpdate(BaseModel):
    """订单更新模型"""
    participant_details: Optional[List[ParticipantDetail]] = None
    booking_date: Optional[datetime] = None
    booking_time: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_phone: Optional[str] = None
    delivery_contact: Optional[str] = None
    delivery_notes: Optional[str] = None
    customer_notes: Optional[str] = None
    merchant_notes: Optional[str] = None
    admin_notes: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    """订单状态更新模型"""
    status: OrderStatus
    notes: Optional[str] = None


class RefundRequest(BaseModel):
    """退款申请模型"""
    reason: str
    amount: Optional[Decimal] = None
    notes: Optional[str] = None
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('退款金额必须大于0')
        return v


class RefundProcess(BaseModel):
    """退款处理模型"""
    status: RefundStatus
    admin_notes: Optional[str] = None
    actual_refund_amount: Optional[Decimal] = None


class OrderResponse(BaseModel):
    """订单响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_number: str
    user_id: int
    order_type: OrderType
    service_id: Optional[int] = None
    product_ids: Optional[str] = None  # JSON string
    bundle_id: Optional[int] = None
    subtotal: Decimal
    discount_amount: Decimal
    coupon_discount: Decimal
    tax_amount: Decimal
    service_fee: Decimal
    total_amount: Decimal
    participant_count: Optional[int] = None
    participant_details: Optional[str] = None  # JSON string
    booking_date: Optional[datetime] = None
    booking_time: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_phone: Optional[str] = None
    delivery_contact: Optional[str] = None
    delivery_notes: Optional[str] = None
    expected_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    status: OrderStatus
    refund_status: RefundStatus
    coupon_code: Optional[str] = None
    promotion_id: Optional[int] = None
    customer_notes: Optional[str] = None
    merchant_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    refund_reason: Optional[str] = None
    refund_amount: Decimal
    refund_requested_at: Optional[datetime] = None
    refund_processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None


class OrderListResponse(BaseModel):
    """订单列表响应模型"""
    id: int
    order_number: str
    order_type: OrderType
    status: OrderStatus
    total_amount: Decimal
    booking_date: Optional[datetime] = None
    created_at: datetime
    service_title: Optional[str] = None  # 关联服务标题
    merchant_name: Optional[str] = None  # 关联商家名称


class OrderSummary(BaseModel):
    """订单摘要模型"""
    total_orders: int
    pending_orders: int
    completed_orders: int
    cancelled_orders: int
    total_revenue: Decimal
    refund_amount: Decimal


class OrderSearchFilter(BaseModel):
    """订单搜索筛选模型"""
    order_type: Optional[OrderType] = None
    status: Optional[OrderStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    service_id: Optional[int] = None
    merchant_id: Optional[int] = None
    keyword: Optional[str] = None 
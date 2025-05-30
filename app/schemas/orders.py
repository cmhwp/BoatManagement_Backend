from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.orders import OrderType, OrderStatus


class OrderBase(BaseModel):
    order_type: OrderType
    service_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: int = 1
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_price: Decimal


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    quantity: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[OrderStatus] = None


class OrderResponse(OrderBase):
    model_config = ConfigDict(from_attributes=True)
    
    order_id: int
    user_id: int
    crew_id: Optional[int] = None
    boat_id: Optional[int] = None
    order_time: datetime
    status: OrderStatus 
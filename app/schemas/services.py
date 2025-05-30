from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ServiceBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Decimal
    duration: Optional[int] = None


class ServiceCreate(ServiceBase):
    merchant_id: int
    boat_id: int


class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    duration: Optional[int] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    model_config = ConfigDict(from_attributes=True)
    
    service_id: int
    merchant_id: int
    boat_id: int
    is_active: bool
    create_time: datetime
    update_time: datetime 
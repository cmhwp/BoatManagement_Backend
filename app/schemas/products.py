from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class ProductBase(BaseModel):
    product_name: str
    description: Optional[str] = None
    price: Decimal
    unit: str
    stock: int = 0
    organic_certified: bool = False
    harvest_date: Optional[date] = None


class ProductCreate(ProductBase):
    merchant_id: int


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    unit: Optional[str] = None
    stock: Optional[int] = None
    organic_certified: Optional[bool] = None
    harvest_date: Optional[date] = None
    is_available: Optional[bool] = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    
    product_id: int
    merchant_id: int
    is_available: bool
    create_time: datetime
    update_time: datetime 
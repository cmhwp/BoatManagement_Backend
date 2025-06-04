from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class MerchantBase(BaseModel):
    """商家基础模式"""
    company_name: str
    business_license_no: str
    legal_representative: Optional[str] = None
    registration_address: Optional[str] = None
    business_address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class MerchantCreate(MerchantBase):
    """商家创建模式"""
    user_id: int
    
    @field_validator('company_name')
    @classmethod
    def validate_company_name(cls, v):
        if len(v) < 2:
            raise ValueError('公司名称不能少于2个字符')
        return v
    
    @field_validator('business_license_no')
    @classmethod
    def validate_business_license_no(cls, v):
        if len(v) < 10:
            raise ValueError('营业执照号格式不正确')
        return v


class MerchantUpdate(BaseModel):
    """商家更新模式"""
    company_name: Optional[str] = None
    business_license_no: Optional[str] = None
    legal_representative: Optional[str] = None
    registration_address: Optional[str] = None
    business_address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class MerchantResponse(MerchantBase):
    """商家响应模式"""
    id: int
    user_id: int
    is_verified: bool
    verification_date: Optional[datetime] = None
    is_active: bool
    rating: float
    total_orders: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MerchantListResponse(BaseModel):
    """商家列表响应模式"""
    id: int
    company_name: str
    is_verified: bool
    rating: float
    total_orders: int
    contact_phone: Optional[str] = None
    
    class Config:
        from_attributes = True


class MerchantVerification(BaseModel):
    """商家认证模式"""
    merchant_id: int
    is_verified: bool
    verification_note: Optional[str] = None 
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.merchant import MerchantStatus, VerificationLevel


class MerchantBase(BaseModel):
    """商家基础模型"""
    business_name: str
    business_license: str
    legal_representative: str
    contact_person: str
    contact_phone: str
    contact_email: str
    business_address: str
    business_scope: str
    
    @field_validator('contact_phone')
    @classmethod
    def validate_phone(cls, v):
        if not v.isdigit() or len(v) != 11:
            raise ValueError('手机号格式不正确')
        return v


class MerchantCreate(MerchantBase):
    """商家创建模型"""
    pass


class MerchantUpdate(BaseModel):
    """商家更新模型"""
    business_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    business_address: Optional[str] = None
    business_scope: Optional[str] = None
    introduction: Optional[str] = None
    logo: Optional[str] = None
    operating_hours: Optional[str] = None
    
    @field_validator('contact_phone')
    @classmethod
    def validate_phone(cls, v):
        if v and (not v.isdigit() or len(v) != 11):
            raise ValueError('手机号格式不正确')
        return v


class MerchantResponse(BaseModel):
    """商家响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    business_name: str
    business_license: str
    legal_representative: str
    contact_person: str
    contact_phone: str
    contact_email: str
    business_address: str
    business_scope: str
    introduction: Optional[str] = None
    logo: Optional[str] = None
    status: MerchantStatus
    verification_level: VerificationLevel
    rating: Optional[Decimal] = None
    total_orders: int
    operating_hours: Optional[str] = None
    location_latitude: Optional[Decimal] = None
    location_longitude: Optional[Decimal] = None
    created_at: datetime
    verified_at: Optional[datetime] = None


class MerchantListResponse(BaseModel):
    """商家列表响应模型"""
    id: int
    business_name: str
    logo: Optional[str] = None
    status: MerchantStatus
    verification_level: VerificationLevel
    rating: Optional[Decimal] = None
    business_address: str
    created_at: datetime


class MerchantVerification(BaseModel):
    """商家认证模型"""
    verification_level: VerificationLevel
    verification_notes: Optional[str] = None 
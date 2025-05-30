from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.merchants import BusinessType


class MerchantBase(BaseModel):
    business_name: str
    license_no: str
    contact_person: str
    business_type: BusinessType


class MerchantCreate(MerchantBase):
    pass


class MerchantUpdate(BaseModel):
    business_name: Optional[str] = None
    license_no: Optional[str] = None
    contact_person: Optional[str] = None
    business_type: Optional[BusinessType] = None


class MerchantResponse(MerchantBase):
    model_config = ConfigDict(from_attributes=True)
    
    merchant_id: int
    user_id: int
    create_time: datetime
    update_time: datetime


class CrewInfoBase(BaseModel):
    certificate_id: str
    boat_type: str


class CrewInfoCreate(CrewInfoBase):
    merchant_id: int


class CrewInfoUpdate(BaseModel):
    certificate_id: Optional[str] = None
    boat_type: Optional[str] = None
    work_status: Optional[str] = None


class CrewInfoResponse(CrewInfoBase):
    model_config = ConfigDict(from_attributes=True)
    
    crew_id: int
    user_id: int
    merchant_id: int
    work_status: str
    create_time: datetime
    update_time: datetime
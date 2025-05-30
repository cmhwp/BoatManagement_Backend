from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.models.boats import BoatStatus


class BoatBase(BaseModel):
    boat_name: str
    boat_type: str
    capacity: int
    gps_id: Optional[str] = None


class BoatCreate(BoatBase):
    merchant_id: int


class BoatUpdate(BaseModel):
    boat_name: Optional[str] = None
    boat_type: Optional[str] = None
    capacity: Optional[int] = None
    gps_id: Optional[str] = None
    status: Optional[BoatStatus] = None


class BoatResponse(BoatBase):
    model_config = ConfigDict(from_attributes=True)
    
    boat_id: int
    merchant_id: int
    status: BoatStatus 
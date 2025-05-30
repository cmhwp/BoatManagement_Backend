from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class BoatStatus(str, enum.Enum):
    free = "free"
    in_use = "in_use"
    maintain = "maintain"


class Boat(Base):
    __tablename__ = "boats"

    boat_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    merchant_id = Column(Integer, ForeignKey("merchants.merchant_id"), nullable=False)
    boat_name = Column(String(50), nullable=False)
    boat_type = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    gps_id = Column(String(50), unique=True)
    status = Column(Enum(BoatStatus), default=BoatStatus.free)

    # 关系
    merchant = relationship("Merchant", back_populates="boats")
    services = relationship("Service", back_populates="boat")
    orders = relationship("Order", back_populates="boat") 
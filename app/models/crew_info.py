from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class WorkStatus(str, enum.Enum):
    free = "free"
    busy = "busy"


class CrewInfo(Base):
    __tablename__ = "crew_info"

    crew_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.merchant_id"), nullable=False)
    certificate_id = Column(String(50), unique=True, nullable=False)
    boat_type = Column(String(50), nullable=False)
    work_status = Column(Enum(WorkStatus), default=WorkStatus.free)
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="crew_info")
    merchant = relationship("Merchant", back_populates="crew_members")
    orders = relationship("Order", back_populates="crew") 
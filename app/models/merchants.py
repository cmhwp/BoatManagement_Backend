from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class BusinessType(str, enum.Enum):
    tourism = "tourism"
    agriculture = "agriculture"
    both = "both"


class Merchant(Base):
    __tablename__ = "merchants"

    merchant_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    business_name = Column(String(100), nullable=False)
    license_no = Column(String(50), unique=True, nullable=False)
    contact_person = Column(String(50), nullable=False)
    business_type = Column(Enum(BusinessType), nullable=False)
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="merchant")
    crew_members = relationship("CrewInfo", back_populates="merchant")
    boats = relationship("Boat", back_populates="merchant")
    services = relationship("Service", back_populates="merchant")
    agricultural_products = relationship("AgriculturalProduct", back_populates="merchant") 
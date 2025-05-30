from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Service(Base):
    __tablename__ = "services"

    service_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    merchant_id = Column(Integer, ForeignKey("merchants.merchant_id"), nullable=False)
    boat_id = Column(Integer, ForeignKey("boats.boat_id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    duration = Column(Integer)  # 预计时长（分钟）
    is_active = Column(Boolean, default=True)
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    merchant = relationship("Merchant", back_populates="services")
    boat = relationship("Boat", back_populates="services")
    orders = relationship("Order", back_populates="service")
    product_bundles = relationship("ServiceProductBundle", back_populates="service") 
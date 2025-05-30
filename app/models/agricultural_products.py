from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class AgriculturalProduct(Base):
    __tablename__ = "agricultural_products"

    product_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    merchant_id = Column(Integer, ForeignKey("merchants.merchant_id"), nullable=False)
    product_name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    stock = Column(Integer, default=0)
    organic_certified = Column(Boolean, default=False)
    harvest_date = Column(Date)
    is_available = Column(Boolean, default=True)
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    merchant = relationship("Merchant", back_populates="agricultural_products")
    orders = relationship("Order", back_populates="product")
    inventory_logs = relationship("InventoryLog", back_populates="product")
    product_bundles = relationship("ServiceProductBundle", back_populates="product") 
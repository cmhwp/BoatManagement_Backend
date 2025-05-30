from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class OrderType(str, enum.Enum):
    service = "service"
    product = "product"
    bundle = "bundle"


class OrderStatus(str, enum.Enum):
    unpaid = "unpaid"
    paid = "paid"
    completed = "completed"
    canceled = "canceled"


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    service_id = Column(Integer, ForeignKey("services.service_id"))
    product_id = Column(Integer, ForeignKey("agricultural_products.product_id"))
    quantity = Column(Integer, default=1)
    crew_id = Column(Integer, ForeignKey("crew_info.crew_id"))
    boat_id = Column(Integer, ForeignKey("boats.boat_id"))
    order_time = Column(DateTime, default=func.now())
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.unpaid)

    # 关系
    user = relationship("User", back_populates="orders")
    service = relationship("Service", back_populates="orders")
    product = relationship("AgriculturalProduct", back_populates="orders")
    crew = relationship("CrewInfo", back_populates="orders")
    boat = relationship("Boat", back_populates="orders")
    inventory_logs = relationship("InventoryLog", back_populates="order") 
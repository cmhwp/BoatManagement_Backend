from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class ChangeType(str, enum.Enum):
    sale = "sale"
    restock = "restock"
    adjust = "adjust"


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("agricultural_products.product_id"), nullable=False)
    change_amount = Column(Integer, nullable=False)  # 变更数量（+入库/-出库）
    change_type = Column(Enum(ChangeType), nullable=False)
    related_order_id = Column(Integer, ForeignKey("orders.order_id"))
    changed_time = Column(DateTime, default=func.now())

    # 关系
    product = relationship("AgriculturalProduct", back_populates="inventory_logs")
    order = relationship("Order", back_populates="inventory_logs") 
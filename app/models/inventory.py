from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class InventoryAction(enum.Enum):
    """库存操作类型枚举"""
    IN = "in"  # 入库
    OUT = "out"  # 出库
    ADJUST = "adjust"  # 调整
    TRANSFER = "transfer"  # 转移
    DAMAGED = "damaged"  # 损坏
    EXPIRED = "expired"  # 过期


class InventoryLog(Base):
    """库存变更日志表"""
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True, comment="日志ID")
    product_id = Column(Integer, ForeignKey("agricultural_products.id"), nullable=False, comment="产品ID")
    
    # 变更信息
    action = Column(Enum(InventoryAction), nullable=False, comment="操作类型")
    quantity_change = Column(Integer, nullable=False, comment="数量变更（正数为增加，负数为减少）")
    quantity_before = Column(Integer, nullable=False, comment="变更前数量")
    quantity_after = Column(Integer, nullable=False, comment="变更后数量")
    
    # 相关信息
    order_id = Column(Integer, comment="相关订单ID")
    operator_id = Column(Integer, comment="操作人ID")
    
    # 备注信息
    reason = Column(String(200), comment="变更原因")
    notes = Column(Text, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="操作时间")
    
    # 关联关系
    product = relationship("AgriculturalProduct", back_populates="inventory_logs")

    def __repr__(self):
        return f"<InventoryLog(id={self.id}, product_id={self.product_id}, action='{self.action}', quantity_change={self.quantity_change})>" 
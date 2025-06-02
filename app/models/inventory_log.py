from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import InventoryAction


class InventoryLog(Base):
    """库存变更日志模型"""
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True, comment="日志ID")
    product_id = Column(Integer, ForeignKey("agricultural_products.id"), nullable=False, comment="产品ID")
    
    # 变更信息
    action = Column(SQLEnum(InventoryAction), nullable=False, comment="操作类型")
    quantity_change = Column(Integer, nullable=False, comment="数量变化")
    quantity_before = Column(Integer, nullable=False, comment="变更前数量")
    quantity_after = Column(Integer, nullable=False, comment="变更后数量")
    
    # 操作信息
    operator_id = Column(Integer, ForeignKey("users.id"), comment="操作人ID")
    reason = Column(String(100), comment="变更原因")
    reference_id = Column(Integer, comment="关联业务ID")
    reference_type = Column(String(50), comment="关联业务类型")
    
    # 备注
    notes = Column(Text, comment="备注")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系
    product = relationship("AgriculturalProduct")
    operator = relationship("User")
    
    def __repr__(self):
        return f"<InventoryLog(id={self.id}, product_id={self.product_id}, action='{self.action}', change={self.quantity_change})>" 
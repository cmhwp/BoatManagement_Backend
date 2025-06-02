from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class InventoryLog(Base):
    """库存变更日志模型"""
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True, comment="库存日志ID")
    product_id = Column(Integer, ForeignKey("agricultural_products.id"), nullable=False, comment="产品ID")
    order_id = Column(Integer, ForeignKey("orders.id"), comment="关联订单ID")
    user_id = Column(Integer, ForeignKey("users.id"), comment="操作用户ID")
    
    # 变更信息
    change_type = Column(String(20), nullable=False, comment="变更类型（入库/出库/调整/损耗）")
    quantity_before = Column(Integer, nullable=False, comment="变更前数量")
    quantity_change = Column(Integer, nullable=False, comment="变更数量（正数为增加，负数为减少）")
    quantity_after = Column(Integer, nullable=False, comment="变更后数量")
    
    # 成本信息
    unit_cost = Column(Numeric(8, 2), comment="单位成本")
    total_cost = Column(Numeric(10, 2), comment="总成本")
    
    # 批次信息
    batch_number = Column(String(50), comment="批次号")
    supplier = Column(String(100), comment="供应商")
    
    # 变更原因
    reason = Column(String(100), comment="变更原因")
    notes = Column(Text, comment="备注")
    reference_number = Column(String(50), comment="参考单号")
    
    # 位置信息
    warehouse_location = Column(String(100), comment="仓库位置")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    operation_date = Column(DateTime, comment="操作日期")
    
    # 关系
    product = relationship("AgriculturalProduct", back_populates="inventory_logs")
    order = relationship("Order")
    user = relationship("User")
    
    def __repr__(self):
        return f"<InventoryLog(id={self.id}, product_id={self.product_id}, change_type='{self.change_type}', quantity_change={self.quantity_change})>" 
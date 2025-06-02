from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Decimal, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class ServiceProductBundle(Base):
    """服务-产品组合关系表"""
    __tablename__ = "service_product_bundles"

    id = Column(Integer, primary_key=True, index=True, comment="套餐ID")
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, comment="服务ID")
    
    # 基本信息
    name = Column(String(200), nullable=False, comment="套餐名称")
    description = Column(Text, comment="套餐描述")
    
    # 包含的产品（JSON格式存储产品ID和数量）
    product_items = Column(Text, comment="包含产品列表（JSON格式：[{product_id, quantity}]）")
    
    # 价格信息
    original_price = Column(Decimal(10, 2), comment="原价总和")
    bundle_price = Column(Decimal(10, 2), nullable=False, comment="套餐价格")
    discount_amount = Column(Decimal(10, 2), comment="优惠金额")
    discount_percentage = Column(Decimal(5, 2), comment="折扣百分比")
    
    # 限制信息
    max_participants = Column(Integer, comment="最大参与人数")
    min_advance_booking_hours = Column(Integer, default=24, comment="最少提前预订小时数")
    
    # 有效期
    valid_from = Column(DateTime, comment="有效开始时间")
    valid_until = Column(DateTime, comment="有效结束时间")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_featured = Column(Boolean, default=False, comment="是否推荐套餐")
    
    # 销售统计
    sales_count = Column(Integer, default=0, comment="销售数量")
    view_count = Column(Integer, default=0, comment="浏览次数")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    service = relationship("Service", back_populates="service_bundles")
    product = relationship("AgriculturalProduct", back_populates="service_bundles")
    orders = relationship("Order", back_populates="bundle")

    def __repr__(self):
        return f"<ServiceProductBundle(id={self.id}, name='{self.name}', bundle_price={self.bundle_price})>" 
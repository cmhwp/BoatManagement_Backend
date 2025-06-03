from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import OrderStatus, OrderType


class Order(Base):
    """订单交易记录模型"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, comment="订单ID")
    order_no = Column(String(50), unique=True, nullable=False, comment="订单号")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="下单用户ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="商家ID")
    
    # 订单基础信息
    order_type = Column(SQLEnum(OrderType), nullable=False, comment="订单类型")
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, comment="订单状态")
    
    # 商品信息
    service_id = Column(Integer, ForeignKey("services.id"), comment="服务ID")
    product_id = Column(Integer, ForeignKey("agricultural_products.id"), comment="农产品ID")
    quantity = Column(Integer, default=1, comment="数量")
    unit_price = Column(Numeric(10, 2), nullable=False, comment="单价")
    
    # 金额信息
    subtotal = Column(Numeric(12, 2), nullable=False, comment="小计金额")
    discount_amount = Column(Numeric(10, 2), default=0, comment="优惠金额")
    total_amount = Column(Numeric(12, 2), nullable=False, comment="总金额")
    
    # 服务时间信息（适用于服务订单）
    service_date = Column(DateTime, comment="服务日期")
    service_time = Column(String(20), comment="服务时间段")
    participants = Column(Integer, comment="参与人数")
    
    # 联系信息
    contact_name = Column(String(50), comment="联系人姓名")
    contact_phone = Column(String(20), comment="联系电话")
    
    # 特殊需求
    special_requirements = Column(Text, comment="特殊需求")
    notes = Column(Text, comment="备注")
    
    # 优惠券信息
    coupon_id = Column(Integer, ForeignKey("coupons.id"), comment="使用的优惠券ID")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="下单时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    confirmed_at = Column(DateTime, comment="确认时间")
    completed_at = Column(DateTime, comment="完成时间")
    cancelled_at = Column(DateTime, comment="取消时间")
    
    # 关系
    user = relationship("User")
    merchant = relationship("Merchant")
    service = relationship("Service")
    product = relationship("AgriculturalProduct")
    coupon = relationship("Coupon")
    payments = relationship("Payment", back_populates="order")
    reviews = relationship("Review", back_populates="order")
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_no='{self.order_no}', type='{self.order_type}', status='{self.status}')>" 
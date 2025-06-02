from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import OrderType, OrderStatus


class Order(Base):
    """订单交易记录模型"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, comment="订单ID")
    order_number = Column(String(50), unique=True, nullable=False, comment="订单号")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="下单用户ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="商家ID")
    
    # 订单基本信息
    order_type = Column(SQLEnum(OrderType), nullable=False, comment="订单类型")
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, comment="订单状态")
    
    # 金额信息
    subtotal = Column(Numeric(10, 2), nullable=False, comment="小计金额")
    discount_amount = Column(Numeric(8, 2), default=0.00, comment="折扣金额")
    shipping_fee = Column(Numeric(6, 2), default=0.00, comment="运费")
    tax_amount = Column(Numeric(8, 2), default=0.00, comment="税费")
    total_amount = Column(Numeric(10, 2), nullable=False, comment="订单总金额")
    paid_amount = Column(Numeric(10, 2), default=0.00, comment="已支付金额")
    
    # 优惠券信息
    coupon_id = Column(Integer, ForeignKey("coupons.id"), comment="使用的优惠券ID")
    coupon_discount = Column(Numeric(8, 2), default=0.00, comment="优惠券折扣金额")
    
    # 联系信息
    contact_name = Column(String(50), comment="联系人姓名")
    contact_phone = Column(String(20), comment="联系电话")
    contact_email = Column(String(100), comment="联系邮箱")
    
    # 配送信息
    delivery_address = Column(Text, comment="配送地址")
    delivery_method = Column(String(50), comment="配送方式")
    expected_delivery_date = Column(DateTime, comment="预期配送日期")
    actual_delivery_date = Column(DateTime, comment="实际配送日期")
    
    # 服务信息（针对服务订单）
    service_date = Column(DateTime, comment="服务日期")
    participant_count = Column(Integer, comment="参与人数")
    special_requirements = Column(Text, comment="特殊要求")
    
    # 备注信息
    customer_notes = Column(Text, comment="客户备注")
    merchant_notes = Column(Text, comment="商家备注")
    admin_notes = Column(Text, comment="管理员备注")
    
    # 评价信息
    is_reviewed = Column(Boolean, default=False, comment="是否已评价")
    review_rating = Column(Numeric(3, 2), comment="评价评分")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="下单时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    confirmed_at = Column(DateTime, comment="确认时间")
    completed_at = Column(DateTime, comment="完成时间")
    cancelled_at = Column(DateTime, comment="取消时间")
    
    # 关系
    user = relationship("User", back_populates="orders")
    merchant = relationship("Merchant")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order")
    coupon = relationship("Coupon")
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', status='{self.status}', total={self.total_amount})>"


class OrderItem(Base):
    """订单项模型"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, comment="订单项ID")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="订单ID")
    
    # 商品信息
    service_id = Column(Integer, ForeignKey("services.id"), comment="服务ID")
    product_id = Column(Integer, ForeignKey("agricultural_products.id"), comment="产品ID")
    
    # 购买信息
    quantity = Column(Integer, nullable=False, comment="数量")
    unit_price = Column(Numeric(8, 2), nullable=False, comment="单价")
    total_price = Column(Numeric(10, 2), nullable=False, comment="小计")
    
    # 商品快照信息（防止商品信息变更影响历史订单）
    item_name = Column(String(100), nullable=False, comment="商品名称快照")
    item_description = Column(Text, comment="商品描述快照")
    item_specifications = Column(Text, comment="商品规格快照，JSON格式")
    
    # 服务相关信息
    service_date = Column(DateTime, comment="服务日期")
    participant_details = Column(Text, comment="参与者详情，JSON格式")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    order = relationship("Order", back_populates="order_items")
    service = relationship("Service", back_populates="order_items")
    product = relationship("AgriculturalProduct", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, item='{self.item_name}', quantity={self.quantity})>" 
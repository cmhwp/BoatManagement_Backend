from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Decimal, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class OrderStatus(enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"  # 待支付
    PAID = "paid"  # 已支付
    CONFIRMED = "confirmed"  # 已确认
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消
    REFUNDED = "refunded"  # 已退款


class OrderType(enum.Enum):
    """订单类型枚举"""
    SERVICE = "service"  # 服务订单
    PRODUCT = "product"  # 产品订单
    BUNDLE = "bundle"  # 套餐订单


class RefundStatus(enum.Enum):
    """退款状态枚举"""
    NONE = "none"  # 无退款
    REQUESTED = "requested"  # 申请退款
    PROCESSING = "processing"  # 处理中
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    COMPLETED = "completed"  # 已完成


class Order(Base):
    """订单交易记录表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, comment="订单ID")
    order_number = Column(String(50), unique=True, nullable=False, comment="订单号")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    
    # 订单内容
    order_type = Column(Enum(OrderType), nullable=False, comment="订单类型")
    service_id = Column(Integer, ForeignKey("services.id"), comment="服务ID")
    product_ids = Column(Text, comment="产品ID列表（JSON格式）")
    bundle_id = Column(Integer, ForeignKey("service_product_bundles.id"), comment="套餐ID")
    
    # 价格信息
    subtotal = Column(Decimal(10, 2), nullable=False, comment="小计金额")
    discount_amount = Column(Decimal(10, 2), default=0.00, comment="折扣金额")
    coupon_discount = Column(Decimal(10, 2), default=0.00, comment="优惠券折扣")
    tax_amount = Column(Decimal(10, 2), default=0.00, comment="税费")
    service_fee = Column(Decimal(10, 2), default=0.00, comment="服务费")
    total_amount = Column(Decimal(10, 2), nullable=False, comment="总金额")
    
    # 参与信息（针对服务订单）
    participant_count = Column(Integer, comment="参与人数")
    participant_details = Column(Text, comment="参与者详情（JSON格式）")
    booking_date = Column(DateTime, comment="预订日期")
    booking_time = Column(String(20), comment="预订时间段")
    
    # 配送信息（针对产品订单）
    delivery_address = Column(Text, comment="配送地址")
    delivery_phone = Column(String(20), comment="配送电话")
    delivery_contact = Column(String(100), comment="收货人姓名")
    delivery_notes = Column(Text, comment="配送备注")
    expected_delivery = Column(DateTime, comment="预计配送时间")
    actual_delivery = Column(DateTime, comment="实际配送时间")
    
    # 状态信息
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, comment="订单状态")
    refund_status = Column(Enum(RefundStatus), default=RefundStatus.NONE, comment="退款状态")
    
    # 优惠信息
    coupon_code = Column(String(50), comment="使用的优惠券代码")
    promotion_id = Column(Integer, comment="促销活动ID")
    
    # 备注信息
    customer_notes = Column(Text, comment="客户备注")
    merchant_notes = Column(Text, comment="商家备注")
    admin_notes = Column(Text, comment="管理员备注")
    
    # 退款信息
    refund_reason = Column(Text, comment="退款原因")
    refund_amount = Column(Decimal(10, 2), default=0.00, comment="退款金额")
    refund_requested_at = Column(DateTime, comment="申请退款时间")
    refund_processed_at = Column(DateTime, comment="处理退款时间")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="下单时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    confirmed_at = Column(DateTime, comment="确认时间")
    completed_at = Column(DateTime, comment="完成时间")
    cancelled_at = Column(DateTime, comment="取消时间")
    
    # 关联关系
    user = relationship("User", back_populates="orders")
    service = relationship("Service", back_populates="orders")
    bundle = relationship("ServiceProductBundle", back_populates="orders")
    payments = relationship("Payment", back_populates="order")
    shippings = relationship("Shipping", back_populates="order")
    reviews = relationship("Review", back_populates="order")

    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', status='{self.status}', total_amount={self.total_amount})>" 
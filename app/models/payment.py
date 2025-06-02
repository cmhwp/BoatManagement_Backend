from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import PaymentStatus, PaymentMethod


class Payment(Base):
    """支付交易记录模型"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, comment="支付ID")
    payment_number = Column(String(50), unique=True, nullable=False, comment="支付流水号")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="关联订单ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="支付用户ID")
    
    # 支付信息
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False, comment="支付方式")
    amount = Column(Numeric(10, 2), nullable=False, comment="支付金额")
    currency = Column(String(10), default="CNY", comment="货币类型")
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, comment="支付状态")
    
    # 第三方支付信息
    external_transaction_id = Column(String(100), comment="第三方交易ID")
    external_payment_id = Column(String(100), comment="第三方支付ID")
    payment_gateway = Column(String(50), comment="支付网关")
    gateway_response = Column(Text, comment="网关响应信息，JSON格式")
    
    # 退款信息
    refund_amount = Column(Numeric(10, 2), default=0.00, comment="退款金额")
    refund_reason = Column(String(255), comment="退款原因")
    refunded_at = Column(DateTime, comment="退款时间")
    
    # 手续费信息
    transaction_fee = Column(Numeric(8, 2), default=0.00, comment="手续费")
    merchant_received = Column(Numeric(10, 2), comment="商家实收金额")
    
    # 备注信息
    payment_notes = Column(Text, comment="支付备注")
    failure_reason = Column(String(255), comment="失败原因")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    paid_at = Column(DateTime, comment="支付成功时间")
    
    # 关系
    order = relationship("Order", back_populates="payments")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, payment_number='{self.payment_number}', amount={self.amount}, status='{self.status}')>" 
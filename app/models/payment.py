from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import PaymentStatus, PaymentMethod


class Payment(Base):
    """支付交易记录模型"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, comment="支付ID")
    payment_no = Column(String(50), unique=True, nullable=False, comment="支付流水号")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="关联订单ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="支付用户ID")
    
    # 支付信息
    amount = Column(Numeric(12, 2), nullable=False, comment="支付金额")
    method = Column(SQLEnum(PaymentMethod), nullable=False, comment="支付方式")
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, comment="支付状态")
    
    # 第三方支付信息
    third_party_transaction_id = Column(String(100), comment="第三方交易ID")
    third_party_response = Column(Text, comment="第三方响应信息(JSON格式)")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    paid_at = Column(DateTime, comment="支付完成时间")
    refunded_at = Column(DateTime, comment="退款时间")
    
    # 备注
    note = Column(Text, comment="支付备注")
    
    # 关系
    order = relationship("Order", back_populates="payments")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, payment_no='{self.payment_no}', amount={self.amount}, status='{self.status}')>" 
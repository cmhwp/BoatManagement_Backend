from sqlalchemy import Column, Integer, String, DateTime, Text, Decimal, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class PaymentMethod(enum.Enum):
    """支付方式枚举"""
    ALIPAY = "alipay"  # 支付宝
    WECHAT = "wechat"  # 微信支付
    UNION_PAY = "union_pay"  # 银联
    BANK_CARD = "bank_card"  # 银行卡
    CASH = "cash"  # 现金
    BALANCE = "balance"  # 账户余额


class PaymentStatus(enum.Enum):
    """支付状态枚举"""
    PENDING = "pending"  # 待支付
    PROCESSING = "processing"  # 支付中
    SUCCESS = "success"  # 支付成功
    FAILED = "failed"  # 支付失败
    CANCELLED = "cancelled"  # 已取消
    REFUNDED = "refunded"  # 已退款


class Payment(Base):
    """支付交易记录表"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, comment="支付记录ID")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="订单ID")
    
    # 支付信息
    payment_number = Column(String(50), unique=True, nullable=False, comment="支付流水号")
    payment_method = Column(Enum(PaymentMethod), nullable=False, comment="支付方式")
    amount = Column(Decimal(10, 2), nullable=False, comment="支付金额")
    
    # 第三方支付信息
    third_party_payment_id = Column(String(100), comment="第三方支付平台订单号")
    third_party_transaction_id = Column(String(100), comment="第三方交易号")
    
    # 支付状态
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, comment="支付状态")
    
    # 时间信息
    initiated_at = Column(DateTime, default=datetime.utcnow, comment="发起支付时间")
    paid_at = Column(DateTime, comment="支付完成时间")
    failed_at = Column(DateTime, comment="支付失败时间")
    
    # 退款信息
    refund_amount = Column(Decimal(10, 2), default=0.00, comment="退款金额")
    refund_reason = Column(Text, comment="退款原因")
    refunded_at = Column(DateTime, comment="退款时间")
    
    # 手续费信息
    platform_fee = Column(Decimal(10, 2), default=0.00, comment="平台手续费")
    payment_fee = Column(Decimal(10, 2), default=0.00, comment="支付手续费")
    
    # 备注信息
    notes = Column(Text, comment="支付备注")
    failure_reason = Column(Text, comment="失败原因")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    order = relationship("Order", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, payment_number='{self.payment_number}', status='{self.status}', amount={self.amount})>" 
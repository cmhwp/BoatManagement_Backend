from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import CouponType


class Coupon(Base):
    """优惠券定义模型"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True, comment="优惠券ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), comment="发放商家ID")
    
    # 基础信息
    name = Column(String(100), nullable=False, comment="优惠券名称")
    code = Column(String(50), unique=True, comment="优惠券码")
    coupon_type = Column(SQLEnum(CouponType), nullable=False, comment="优惠券类型")
    
    # 优惠信息
    discount_value = Column(Numeric(10, 2), comment="优惠金额/折扣值")
    min_amount = Column(Numeric(10, 2), comment="最低消费金额")
     
    # 使用限制
    total_quantity = Column(Integer, comment="发放总量")
    used_quantity = Column(Integer, default=0, comment="已使用数量")
    per_user_limit = Column(Integer, default=1, comment="每用户限制数量")
    
    # 有效期
    start_date = Column(DateTime, nullable=False, comment="开始时间")
    end_date = Column(DateTime, nullable=False, comment="结束时间")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 描述
    description = Column(Text, comment="使用说明")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    merchant = relationship("Merchant")
    user_coupons = relationship("UserCoupon", back_populates="coupon")
    
    def __repr__(self):
        return f"<Coupon(id={self.id}, name='{self.name}', type='{self.coupon_type}')>"


class UserCoupon(Base):
    """用户优惠券持有记录模型"""
    __tablename__ = "user_coupons"

    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False, comment="优惠券ID")
    
    # 状态信息
    is_used = Column(Boolean, default=False, comment="是否已使用")
    used_at = Column(DateTime, comment="使用时间")
    order_id = Column(Integer, ForeignKey("orders.id"), comment="使用的订单ID")
    
    # 获取方式
    source = Column(String(50), comment="获取来源")
    
    # 时间字段
    obtained_at = Column(DateTime, server_default=func.now(), comment="获取时间")
    
    # 关系
    user = relationship("User")
    coupon = relationship("Coupon", back_populates="user_coupons")
    order = relationship("Order")
    
    def __repr__(self):
        return f"<UserCoupon(id={self.id}, user_id={self.user_id}, coupon_id={self.coupon_id}, is_used={self.is_used})>" 
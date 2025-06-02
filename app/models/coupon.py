from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import CouponType, CouponStatus


class Coupon(Base):
    """优惠券定义模型"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True, comment="优惠券ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), comment="发放商家ID（null表示平台券）")
    
    # 基本信息
    name = Column(String(100), nullable=False, comment="优惠券名称")
    code = Column(String(20), unique=True, comment="优惠券代码")
    coupon_type = Column(SQLEnum(CouponType), nullable=False, comment="优惠券类型")
    description = Column(Text, comment="优惠券描述")
    
    # 优惠信息
    discount_value = Column(Numeric(8, 2), nullable=False, comment="折扣值")
    minimum_amount = Column(Numeric(8, 2), default=0.00, comment="最低消费金额")
    maximum_discount = Column(Numeric(8, 2), comment="最大折扣金额")
    
    # 发放限制
    total_quantity = Column(Integer, nullable=False, comment="发放总数量")
    issued_quantity = Column(Integer, default=0, comment="已发放数量")
    used_quantity = Column(Integer, default=0, comment="已使用数量")
    per_user_limit = Column(Integer, default=1, comment="每用户限领数量")
    
    # 使用限制
    applicable_services = Column(Text, comment="适用服务，JSON格式")
    applicable_products = Column(Text, comment="适用产品，JSON格式")
    user_level_required = Column(String(20), comment="要求用户等级")
    
    # 时间限制
    valid_from = Column(DateTime, nullable=False, comment="有效期开始")
    valid_until = Column(DateTime, nullable=False, comment="有效期结束")
    
    # 状态信息
    status = Column(SQLEnum(CouponStatus), default=CouponStatus.ACTIVE, comment="优惠券状态")
    is_stackable = Column(Boolean, default=False, comment="是否可叠加使用")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    merchant = relationship("Merchant")
    user_coupons = relationship("UserCoupon", back_populates="coupon")
    
    def __repr__(self):
        return f"<Coupon(id={self.id}, name='{self.name}', type='{self.coupon_type}', value={self.discount_value})>"


class UserCoupon(Base):
    """用户优惠券持有记录模型"""
    __tablename__ = "user_coupons"

    id = Column(Integer, primary_key=True, index=True, comment="用户优惠券ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False, comment="优惠券ID")
    order_id = Column(Integer, ForeignKey("orders.id"), comment="使用的订单ID")
    
    # 获取信息
    obtained_from = Column(String(50), comment="获取方式（注册赠送/活动获得/手动发放等）")
    
    # 使用信息
    is_used = Column(Boolean, default=False, comment="是否已使用")
    used_at = Column(DateTime, comment="使用时间")
    discount_amount = Column(Numeric(8, 2), comment="实际折扣金额")
    
    # 状态信息
    is_expired = Column(Boolean, default=False, comment="是否已过期")
    
    # 时间字段
    obtained_at = Column(DateTime, server_default=func.now(), comment="获得时间")
    expires_at = Column(DateTime, comment="过期时间")
    
    # 关系
    user = relationship("User", back_populates="user_coupons")
    coupon = relationship("Coupon", back_populates="user_coupons")
    order = relationship("Order")
    
    def __repr__(self):
        return f"<UserCoupon(id={self.id}, user_id={self.user_id}, coupon_id={self.coupon_id}, is_used={self.is_used})>" 
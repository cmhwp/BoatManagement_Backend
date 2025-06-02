from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Decimal, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class CouponType(enum.Enum):
    """优惠券类型枚举"""
    DISCOUNT_AMOUNT = "discount_amount"  # 固定金额折扣
    DISCOUNT_PERCENT = "discount_percent"  # 百分比折扣
    FREE_SHIPPING = "free_shipping"  # 免运费
    BUNDLE_OFFER = "bundle_offer"  # 套餐优惠


class CouponStatus(enum.Enum):
    """优惠券状态枚举"""
    ACTIVE = "active"  # 有效
    INACTIVE = "inactive"  # 无效
    EXPIRED = "expired"  # 已过期
    USED_UP = "used_up"  # 已用完


class UserCouponStatus(enum.Enum):
    """用户优惠券状态枚举"""
    AVAILABLE = "available"  # 可使用
    USED = "used"  # 已使用
    EXPIRED = "expired"  # 已过期


class Coupon(Base):
    """优惠券定义表"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True, comment="优惠券ID")
    
    # 基本信息
    name = Column(String(200), nullable=False, comment="优惠券名称")
    code = Column(String(50), unique=True, nullable=False, comment="优惠券代码")
    description = Column(Text, comment="优惠券描述")
    
    # 优惠信息
    coupon_type = Column(Enum(CouponType), nullable=False, comment="优惠券类型")
    discount_amount = Column(Decimal(10, 2), comment="折扣金额")
    discount_percent = Column(Decimal(5, 2), comment="折扣百分比")
    
    # 使用条件
    min_order_amount = Column(Decimal(10, 2), comment="最低订单金额")
    max_discount_amount = Column(Decimal(10, 2), comment="最大折扣金额")
    applicable_services = Column(Text, comment="适用服务ID列表（JSON格式）")
    applicable_products = Column(Text, comment="适用产品ID列表（JSON格式）")
    
    # 发放信息
    total_quantity = Column(Integer, comment="发放总数量（null表示无限制）")
    used_quantity = Column(Integer, default=0, comment="已使用数量")
    per_user_limit = Column(Integer, default=1, comment="每用户限用次数")
    
    # 有效期
    start_date = Column(DateTime, nullable=False, comment="开始时间")
    end_date = Column(DateTime, nullable=False, comment="结束时间")
    
    # 状态信息
    status = Column(Enum(CouponStatus), default=CouponStatus.ACTIVE, comment="优惠券状态")
    is_public = Column(Boolean, default=True, comment="是否公开（用户可主动领取）")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")
    
    # 关联关系
    user_coupons = relationship("UserCoupon", back_populates="coupon")

    def __repr__(self):
        return f"<Coupon(id={self.id}, code='{self.code}', type='{self.coupon_type}', status='{self.status}')>"


class UserCoupon(Base):
    """用户优惠券持有记录表"""
    __tablename__ = "user_coupons"

    id = Column(Integer, primary_key=True, index=True, comment="用户优惠券ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False, comment="优惠券ID")
    
    # 使用信息
    order_id = Column(Integer, comment="使用的订单ID")
    used_at = Column(DateTime, comment="使用时间")
    
    # 状态信息
    status = Column(Enum(UserCouponStatus), default=UserCouponStatus.AVAILABLE, comment="状态")
    
    # 时间戳
    obtained_at = Column(DateTime, default=datetime.now(), comment="获得时间")
    expires_at = Column(DateTime, comment="过期时间")
    
    # 关联关系
    user = relationship("User", back_populates="user_coupons")
    coupon = relationship("Coupon", back_populates="user_coupons")

    def __repr__(self):
        return f"<UserCoupon(id={self.id}, user_id={self.user_id}, coupon_id={self.coupon_id}, status='{self.status}')>" 
from sqlalchemy import Column, Integer, String, DateTime, Text, Decimal, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class ShippingStatus(enum.Enum):
    """物流状态枚举"""
    PENDING = "pending"  # 待发货
    PICKED_UP = "picked_up"  # 已取件
    IN_TRANSIT = "in_transit"  # 运输中
    OUT_FOR_DELIVERY = "out_for_delivery"  # 派送中
    DELIVERED = "delivered"  # 已送达
    FAILED = "failed"  # 配送失败
    RETURNED = "returned"  # 已退回


class ShippingMethod(enum.Enum):
    """配送方式枚举"""
    EXPRESS = "express"  # 快递
    LOGISTICS = "logistics"  # 物流
    SELF_PICKUP = "self_pickup"  # 自提
    LOCAL_DELIVERY = "local_delivery"  # 同城配送


class Shipping(Base):
    """农产品物流信息表"""
    __tablename__ = "shippings"

    id = Column(Integer, primary_key=True, index=True, comment="物流ID")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="订单ID")
    
    # 物流基本信息
    tracking_number = Column(String(100), unique=True, comment="物流单号")
    shipping_method = Column(Enum(ShippingMethod), nullable=False, comment="配送方式")
    carrier_company = Column(String(100), comment="承运公司")
    carrier_phone = Column(String(20), comment="承运人电话")
    
    # 发货信息
    sender_name = Column(String(100), comment="发货人姓名")
    sender_phone = Column(String(20), comment="发货人电话")
    sender_address = Column(Text, comment="发货地址")
    
    # 收货信息
    receiver_name = Column(String(100), comment="收货人姓名")
    receiver_phone = Column(String(20), comment="收货人电话")
    receiver_address = Column(Text, comment="收货地址")
    
    # 物流状态
    status = Column(Enum(ShippingStatus), default=ShippingStatus.PENDING, comment="物流状态")
    
    # 费用信息
    shipping_fee = Column(Decimal(10, 2), comment="运费")
    insurance_fee = Column(Decimal(10, 2), default=0.00, comment="保价费")
    total_weight = Column(Decimal(8, 3), comment="总重量（kg）")
    
    # 时间信息
    estimated_delivery = Column(DateTime, comment="预计送达时间")
    actual_delivery = Column(DateTime, comment="实际送达时间")
    shipped_at = Column(DateTime, comment="发货时间")
    
    # 物流跟踪
    current_location = Column(String(200), comment="当前位置")
    tracking_info = Column(Text, comment="跟踪信息（JSON格式存储跟踪记录）")
    
    # 配送要求
    delivery_instructions = Column(Text, comment="配送要求")
    special_requirements = Column(Text, comment="特殊要求（如保温、冷链等）")
    
    # 签收信息
    signed_by = Column(String(100), comment="签收人")
    signature_image = Column(String(500), comment="签收图片URL")
    delivery_photos = Column(Text, comment="配送照片（JSON格式存储URL列表）")
    
    # 问题处理
    issues = Column(Text, comment="配送问题（JSON格式）")
    resolution = Column(Text, comment="问题解决方案")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")
    
    # 关联关系
    order = relationship("Order", back_populates="shippings")

    def __repr__(self):
        return f"<Shipping(id={self.id}, tracking_number='{self.tracking_number}', status='{self.status}')>" 
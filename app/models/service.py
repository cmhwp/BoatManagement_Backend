from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Decimal, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class ServiceStatus(enum.Enum):
    """服务状态枚举"""
    ACTIVE = "active"  # 可预订
    INACTIVE = "inactive"  # 暂停服务
    FULL = "full"  # 预订满员
    CANCELLED = "cancelled"  # 已取消


class ServiceType(enum.Enum):
    """服务类型枚举"""
    SIGHTSEEING = "sightseeing"  # 观光游览
    FISHING = "fishing"  # 钓鱼体验
    ADVENTURE = "adventure"  # 探险活动
    DINING = "dining"  # 餐饮服务
    TRANSPORTATION = "transportation"  # 交通接送
    PACKAGE = "package"  # 套餐服务


class Service(Base):
    """旅游服务项目表"""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True, comment="服务ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="商家ID")
    boat_id = Column(Integer, ForeignKey("boats.id"), comment="关联船艇ID")
    region_id = Column(Integer, ForeignKey("regions.id"), comment="服务地区ID")
    
    # 基本信息
    title = Column(String(200), nullable=False, comment="服务标题")
    description = Column(Text, comment="服务描述")
    service_type = Column(Enum(ServiceType), nullable=False, comment="服务类型")
    
    # 价格信息
    price = Column(Decimal(10, 2), nullable=False, comment="服务价格")
    original_price = Column(Decimal(10, 2), comment="原价")
    price_unit = Column(String(20), default="person", comment="价格单位（person/hour/day）")
    
    # 服务详情
    duration = Column(Integer, comment="服务时长（分钟）")
    max_participants = Column(Integer, comment="最大参与人数")
    min_participants = Column(Integer, default=1, comment="最小参与人数")
    age_requirement = Column(String(50), comment="年龄要求")
    
    # 包含内容
    includes = Column(Text, comment="包含内容（JSON格式存储列表）")
    excludes = Column(Text, comment="不包含内容（JSON格式存储列表）")
    requirements = Column(Text, comment="参与要求（JSON格式存储列表）")
    
    # 时间安排
    schedule_type = Column(String(20), default="fixed", comment="排期类型（fixed/flexible）")
    available_times = Column(Text, comment="可用时间段（JSON格式）")
    advance_booking_hours = Column(Integer, default=24, comment="提前预订小时数")
    
    # 位置信息
    meeting_point = Column(String(200), comment="集合地点")
    route_description = Column(Text, comment="路线描述")
    
    # 媒体资源
    images = Column(Text, comment="服务图片（JSON格式存储URL列表）")
    videos = Column(Text, comment="服务视频（JSON格式存储URL列表）")
    
    # 状态信息
    status = Column(Enum(ServiceStatus), default=ServiceStatus.ACTIVE, comment="服务状态")
    is_featured = Column(Boolean, default=False, comment="是否推荐服务")
    is_green_service = Column(Boolean, default=False, comment="是否绿色服务")
    
    # 评价信息
    rating = Column(Decimal(3, 2), default=0.00, comment="服务评分")
    review_count = Column(Integer, default=0, comment="评价数量")
    booking_count = Column(Integer, default=0, comment="预订次数")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    merchant = relationship("Merchant", back_populates="services")
    boat = relationship("Boat", back_populates="services")
    region = relationship("Region", back_populates="services")
    service_bundles = relationship("ServiceProductBundle", back_populates="service")
    orders = relationship("Order", back_populates="service")
    reviews = relationship("Review", back_populates="service")
    schedules = relationship("Schedule", back_populates="service")

    def __repr__(self):
        return f"<Service(id={self.id}, title='{self.title}', type='{self.service_type}', status='{self.status}')>" 
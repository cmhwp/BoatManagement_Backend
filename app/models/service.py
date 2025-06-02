from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import ServiceType, ServiceStatus


class Service(Base):
    """旅游服务项目模型"""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True, comment="服务ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="所属商家ID")
    
    # 基本信息
    name = Column(String(100), nullable=False, comment="服务名称")
    service_type = Column(SQLEnum(ServiceType), nullable=False, comment="服务类型")
    subtitle = Column(String(255), comment="副标题")
    description = Column(Text, comment="服务描述")
    highlights = Column(Text, comment="服务亮点，JSON格式")
    
    # 价格信息
    base_price = Column(Numeric(8, 2), nullable=False, comment="基础价格")
    adult_price = Column(Numeric(8, 2), comment="成人价格")
    child_price = Column(Numeric(8, 2), comment="儿童价格")
    senior_price = Column(Numeric(8, 2), comment="老人价格")
    group_discount_rate = Column(Numeric(5, 2), comment="团体折扣率")
    
    # 服务详情
    duration = Column(Integer, comment="服务时长(分钟)")
    max_participants = Column(Integer, comment="最大参与人数")
    min_participants = Column(Integer, default=1, comment="最小参与人数")
    age_restriction = Column(String(50), comment="年龄限制")
    difficulty_level = Column(String(20), comment="难度等级")
    
    # 行程信息
    itinerary = Column(Text, comment="行程安排，JSON格式")
    meeting_point = Column(String(255), comment="集合地点")
    departure_times = Column(Text, comment="出发时间，JSON格式")
    route_map = Column(String(255), comment="路线图URL")
    
    # 包含内容
    inclusions = Column(Text, comment="包含项目，JSON格式")
    exclusions = Column(Text, comment="不包含项目，JSON格式")
    equipment_provided = Column(Text, comment="提供设备，JSON格式")
    requirements = Column(Text, comment="参与要求，JSON格式")
    
    # 季节性信息
    seasonal_availability = Column(Text, comment="季节性可用性，JSON格式")
    weather_dependent = Column(Boolean, default=False, comment="是否受天气影响")
    
    # 媒体信息
    cover_image = Column(String(255), comment="封面图片URL")
    gallery_images = Column(Text, comment="图片画廊URLs，JSON格式")
    video_url = Column(String(255), comment="介绍视频URL")
    
    # 评级信息
    rating = Column(Numeric(3, 2), default=0.00, comment="平均评分")
    total_reviews = Column(Integer, default=0, comment="总评价数")
    total_bookings = Column(Integer, default=0, comment="总预订数")
    
    # 运营信息
    advance_booking_hours = Column(Integer, default=24, comment="提前预订小时数")
    cancellation_policy = Column(Text, comment="取消政策")
    refund_policy = Column(Text, comment="退款政策")
    
    # 状态信息
    status = Column(SQLEnum(ServiceStatus), default=ServiceStatus.ACTIVE, comment="服务状态")
    is_featured = Column(Boolean, default=False, comment="是否推荐")
    sort_order = Column(Integer, default=0, comment="排序")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    merchant = relationship("Merchant", back_populates="services")
    order_items = relationship("OrderItem", back_populates="service")
    reviews = relationship("Review", back_populates="service")
    
    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.name}', type='{self.service_type}', price={self.base_price})>" 
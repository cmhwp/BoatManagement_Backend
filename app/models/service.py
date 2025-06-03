from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import ServiceStatus, ServiceType


class Service(Base):
    """旅游服务项目模型"""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True, comment="服务ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="提供商家ID")
    
    # 基础信息
    name = Column(String(100), nullable=False, comment="服务名称")
    service_type = Column(SQLEnum(ServiceType), nullable=False, comment="服务类型")
    description = Column(Text, comment="服务描述")
    features = Column(Text, comment="服务特色(JSON格式)")
    
    # 价格信息
    base_price = Column(Numeric(10, 2), nullable=False, comment="基础价格")
    child_price = Column(Numeric(10, 2), comment="儿童价格")
    group_discount = Column(Numeric(5, 2), comment="团体折扣")
    
    # 服务详情
    duration = Column(Integer, comment="服务时长(分钟)")
    max_participants = Column(Integer, comment="最大参与人数")
    min_participants = Column(Integer, comment="最小参与人数")
    
    # 地理信息
    location = Column(String(200), comment="服务地点")
    route_description = Column(Text, comment="路线描述")
    meeting_point = Column(String(200), comment="集合地点")
    
    # 状态信息
    status = Column(SQLEnum(ServiceStatus), default=ServiceStatus.ACTIVE, comment="服务状态")
    
    # 预订信息
    advance_booking_days = Column(Integer, default=1, comment="提前预订天数")
    cancellation_policy = Column(Text, comment="取消政策")
    
    # 评价信息
    rating = Column(Numeric(3, 2), default=0.0, comment="服务评分")
    total_bookings = Column(Integer, default=0, comment="总预订数")
    
    # 媒体信息
    images = Column(Text, comment="服务图片URLs(JSON格式)")
    videos = Column(Text, comment="服务视频URLs(JSON格式)")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    merchant = relationship("Merchant", back_populates="services")
    
    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.name}', type='{self.service_type}', status='{self.status}')>" 
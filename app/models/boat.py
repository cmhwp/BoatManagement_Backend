from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import BoatStatus, BoatType


class Boat(Base):
    """船艇资产信息模型"""
    __tablename__ = "boats"

    id = Column(Integer, primary_key=True, index=True, comment="船艇ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="所属商家ID")
    
    # 基础信息
    name = Column(String(100), nullable=False, comment="船艇名称")
    boat_type = Column(SQLEnum(BoatType), nullable=False, comment="船艇类型")
    registration_no = Column(String(50), unique=True, nullable=False, comment="注册编号")
    license_no = Column(String(50), comment="许可证号")
    
    # 技术参数
    length = Column(Numeric(8, 2), comment="船长(米)")
    width = Column(Numeric(8, 2), comment="船宽(米)")
    passenger_capacity = Column(Integer, comment="载客量")
    cargo_capacity = Column(Numeric(10, 2), comment="载货量(吨)")
    engine_power = Column(String(50), comment="发动机功率")
    fuel_type = Column(String(20), comment="燃料类型")
    
    # 状态信息
    status = Column(SQLEnum(BoatStatus), default=BoatStatus.AVAILABLE, comment="船艇状态")
    current_location = Column(String(200), comment="当前位置")
    last_maintenance = Column(DateTime, comment="上次维护时间")
    next_maintenance = Column(DateTime, comment="下次维护时间")
    
    # 安全信息
    safety_equipment = Column(Text, comment="安全设备清单(JSON格式)")
    insurance_no = Column(String(50), comment="保险单号")
    insurance_expiry = Column(DateTime, comment="保险到期时间")
    
    # 运营信息
    daily_rate = Column(Numeric(10, 2), comment="日租金")
    hourly_rate = Column(Numeric(8, 2), comment="小时租金")
    is_available = Column(Boolean, default=True, comment="是否可用")
    
    # 描述信息
    description = Column(Text, comment="船艇描述")
    images = Column(Text, comment="船艇图片URLs(JSON格式)")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    merchant = relationship("Merchant", back_populates="boats")
    schedules = relationship("Schedule", back_populates="boat")
    
    def __repr__(self):
        return f"<Boat(id={self.id}, name='{self.name}', type='{self.boat_type}', status='{self.status}')>" 
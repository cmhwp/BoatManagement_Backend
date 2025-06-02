from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Decimal, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class BoatStatus(enum.Enum):
    """船艇状态枚举"""
    AVAILABLE = "available"  # 可用
    OCCUPIED = "occupied"  # 使用中
    MAINTENANCE = "maintenance"  # 维护中
    RETIRED = "retired"  # 退役


class BoatType(enum.Enum):
    """船艇类型枚举"""
    SIGHTSEEING = "sightseeing"  # 观光船
    FISHING = "fishing"  # 钓鱼船
    SPEEDBOAT = "speedboat"  # 快艇
    YACHT = "yacht"  # 游艇
    CARGO = "cargo"  # 货船


class Boat(Base):
    """船艇资产信息表"""
    __tablename__ = "boats"

    id = Column(Integer, primary_key=True, index=True, comment="船艇ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="所属商家ID")
    
    # 基本信息
    name = Column(String(100), nullable=False, comment="船艇名称")
    registration_number = Column(String(50), unique=True, comment="船舶登记号")
    boat_type = Column(Enum(BoatType), nullable=False, comment="船艇类型")
    model = Column(String(100), comment="船艇型号")
    manufacturer = Column(String(100), comment="制造商")
    
    # 技术参数
    length = Column(Decimal(5, 2), comment="船长（米）")
    width = Column(Decimal(5, 2), comment="船宽（米）")
    max_capacity = Column(Integer, comment="最大载客量")
    max_speed = Column(Decimal(5, 2), comment="最大航速（节）")
    fuel_type = Column(String(50), comment="燃料类型")
    
    # 设施设备
    amenities = Column(Text, comment="船上设施（JSON格式存储设施列表）")
    safety_equipment = Column(Text, comment="安全设备（JSON格式）")
    images = Column(Text, comment="船艇图片（JSON格式存储URL列表）")
    
    # 证照信息
    license_number = Column(String(50), comment="船舶证书号")
    license_expire_date = Column(DateTime, comment="证书到期时间")
    insurance_number = Column(String(50), comment="保险单号")
    insurance_expire_date = Column(DateTime, comment="保险到期时间")
    
    # 运营信息
    status = Column(Enum(BoatStatus), default=BoatStatus.AVAILABLE, comment="船艇状态")
    is_green_certified = Column(Boolean, default=False, comment="是否绿色认证")
    hourly_rate = Column(Decimal(10, 2), comment="小时租金")
    daily_rate = Column(Decimal(10, 2), comment="日租金")
    
    # 位置信息
    home_port = Column(String(100), comment="母港")
    current_location = Column(String(100), comment="当前位置")
    gps_coordinates = Column(String(50), comment="GPS坐标")
    
    # 维护信息
    last_maintenance = Column(DateTime, comment="最后维护时间")
    next_maintenance = Column(DateTime, comment="下次维护时间")
    maintenance_notes = Column(Text, comment="维护备注")
    
    # 时间戳
    purchase_date = Column(DateTime, comment="购买时间")
    created_at = Column(DateTime, default=datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")
    
    # 关联关系
    merchant = relationship("Merchant", back_populates="boats")
    services = relationship("Service", back_populates="boat")
    schedules = relationship("Schedule", back_populates="boat")
    current_crew_members = relationship("CrewInfo", back_populates="current_boat")

    def __repr__(self):
        return f"<Boat(id={self.id}, name='{self.name}', type='{self.boat_type}', status='{self.status}')>" 
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import BoatStatus, BoatType


class Boat(Base):
    """船艇资产信息模型"""
    __tablename__ = "boats"

    id = Column(Integer, primary_key=True, index=True, comment="船艇ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="所属商家ID")
    
    # 基本信息
    name = Column(String(100), nullable=False, comment="船艇名称")
    boat_type = Column(SQLEnum(BoatType), nullable=False, comment="船艇类型")
    registration_number = Column(String(50), unique=True, comment="船舶注册号")
    model = Column(String(100), comment="船艇型号")
    manufacturer = Column(String(100), comment="制造商")
    
    # 技术参数
    length = Column(Numeric(8, 2), comment="船长(米)")
    width = Column(Numeric(8, 2), comment="船宽(米)")
    draft = Column(Numeric(8, 2), comment="吃水深度(米)")
    gross_tonnage = Column(Numeric(10, 2), comment="总吨位")
    max_speed = Column(Numeric(6, 2), comment="最大航速(节)")
    fuel_capacity = Column(Numeric(8, 2), comment="燃料容量(升)")
    
    # 载客信息
    passenger_capacity = Column(Integer, comment="载客量")
    crew_capacity = Column(Integer, comment="船员数量")
    cabin_count = Column(Integer, comment="舱室数量")
    
    # 设备信息
    equipment_list = Column(Text, comment="设备清单，JSON格式")
    safety_equipment = Column(Text, comment="安全设备，JSON格式")
    navigation_equipment = Column(Text, comment="导航设备，JSON格式")
    
    # 证照信息
    certificate_number = Column(String(50), comment="船舶证书号")
    certificate_expiry = Column(DateTime, comment="证书到期日期")
    insurance_number = Column(String(50), comment="保险单号")
    insurance_expiry = Column(DateTime, comment="保险到期日期")
    
    # 位置信息
    current_location = Column(String(255), comment="当前位置")
    home_port = Column(String(100), comment="母港")
    gps_coordinates = Column(String(100), comment="GPS坐标")
    
    # 运营信息
    purchase_date = Column(DateTime, comment="购买日期")
    purchase_price = Column(Numeric(12, 2), comment="购买价格")
    current_value = Column(Numeric(12, 2), comment="当前价值")
    daily_rental_rate = Column(Numeric(8, 2), comment="日租金")
    hourly_rental_rate = Column(Numeric(8, 2), comment="小时租金")
    
    # 维护信息
    last_maintenance_date = Column(DateTime, comment="上次维护日期")
    next_maintenance_date = Column(DateTime, comment="下次维护日期")
    total_operating_hours = Column(Integer, default=0, comment="总运行小时数")
    maintenance_notes = Column(Text, comment="维护记录")
    
    # 状态信息
    status = Column(SQLEnum(BoatStatus), default=BoatStatus.AVAILABLE, comment="船艇状态")
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 媒体信息
    images = Column(Text, comment="船艇图片URLs，JSON格式")
    documents = Column(Text, comment="相关文档URLs，JSON格式")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    merchant = relationship("Merchant", back_populates="boats")
    schedules = relationship("Schedule", back_populates="boat")
    
    def __repr__(self):
        return f"<Boat(id={self.id}, name='{self.name}', type='{self.boat_type}', status='{self.status}')>" 
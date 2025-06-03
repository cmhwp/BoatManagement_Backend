from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class CrewInfo(Base):
    """船员专业信息模型"""
    __tablename__ = "crew_info"

    id = Column(Integer, primary_key=True, index=True, comment="船员信息ID")
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="关联用户ID")
    
    # 基础信息
    id_card_no = Column(String(20), unique=True, nullable=False, comment="身份证号")
    license_no = Column(String(50), unique=True, comment="船员证书号")
    license_type = Column(String(50), comment="证书类型")
    license_expiry = Column(DateTime, comment="证书到期时间")
    
    # 专业能力
    years_of_experience = Column(Integer, default=0, comment="从业年限")
    specialties = Column(Text, comment="专业技能(JSON格式)")
    
    # 工作状态
    is_available = Column(Boolean, default=True, comment="是否可用")
    current_status = Column(String(20), default="available", comment="当前状态")
    
    # 评价信息
    rating = Column(Numeric(3, 2), default=0.0, comment="船员评分")
    total_services = Column(Integer, default=0, comment="总服务次数")
    
    # 紧急联系人
    emergency_contact = Column(String(50), comment="紧急联系人")
    emergency_phone = Column(String(20), comment="紧急联系电话")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="crew_info")
    schedules = relationship("Schedule", back_populates="crew")
    
    def __repr__(self):
        return f"<CrewInfo(id={self.id}, license_no='{self.license_no}', is_available={self.is_available})>" 
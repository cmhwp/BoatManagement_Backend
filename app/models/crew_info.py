from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class CrewInfo(Base):
    """船员专业信息模型"""
    __tablename__ = "crew_info"

    id = Column(Integer, primary_key=True, index=True, comment="船员信息ID")
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="关联用户ID")
    
    # 基本信息
    crew_number = Column(String(50), unique=True, comment="船员编号")
    position = Column(String(50), comment="职位")
    level = Column(String(20), comment="等级")
    specialties = Column(Text, comment="专业技能，JSON格式")
    
    # 证书信息
    license_number = Column(String(50), comment="船员证书号")
    license_type = Column(String(50), comment="证书类型")
    license_issue_date = Column(DateTime, comment="证书签发日期")
    license_expiry_date = Column(DateTime, comment="证书到期日期")
    
    # 工作信息
    work_experience = Column(Integer, default=0, comment="工作经验年数")
    current_employer = Column(String(100), comment="当前雇主")
    emergency_contact = Column(String(100), comment="紧急联系人")
    emergency_phone = Column(String(20), comment="紧急联系电话")
    
    # 健康信息
    health_certificate_number = Column(String(50), comment="健康证号")
    health_expiry_date = Column(DateTime, comment="健康证到期日期")
    medical_restrictions = Column(Text, comment="医疗限制")
    
    # 评级信息
    rating = Column(Numeric(3, 2), default=0.00, comment="平均评分")
    total_reviews = Column(Integer, default=0, comment="总评价数")
    total_working_hours = Column(Integer, default=0, comment="总工作小时数")
    
    # 状态信息
    is_available = Column(Boolean, default=True, comment="是否可用")
    is_certified = Column(Boolean, default=False, comment="是否已认证")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="crew_info")
    schedules = relationship("Schedule", back_populates="crew")
    certificates = relationship("Certificate", back_populates="crew")
    
    def __repr__(self):
        return f"<CrewInfo(id={self.id}, crew_number='{self.crew_number}', position='{self.position}')>" 
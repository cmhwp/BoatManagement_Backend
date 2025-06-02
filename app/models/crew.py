from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class CrewStatus(enum.Enum):
    """船员状态枚举"""
    ACTIVE = "active"  # 在岗
    INACTIVE = "inactive"  # 离岗
    SUSPENDED = "suspended"  # 暂停
    TRAINING = "training"  # 培训中


class CrewLevel(enum.Enum):
    """船员等级枚举"""
    TRAINEE = "trainee"  # 实习船员
    JUNIOR = "junior"  # 初级船员
    SENIOR = "senior"  # 高级船员
    CAPTAIN = "captain"  # 船长


class CrewInfo(Base):
    """船员专业信息表"""
    __tablename__ = "crew_info"

    id = Column(Integer, primary_key=True, index=True, comment="船员信息ID")
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="关联用户ID")
    
    # 船员资质
    license_number = Column(String(50), unique=True, comment="船员证书号")
    license_type = Column(String(50), comment="证书类型")
    license_level = Column(Enum(CrewLevel), default=CrewLevel.TRAINEE, comment="船员等级")
    license_expire_date = Column(DateTime, comment="证书到期时间")
    
    # 专业技能
    specialties = Column(Text, comment="专业技能（JSON格式存储技能列表）")
    languages = Column(Text, comment="语言能力（JSON格式）")
    experience_years = Column(Integer, default=0, comment="从业年限")
    
    # 健康信息
    health_certificate = Column(String(255), comment="健康证明文件URL")
    health_expire_date = Column(DateTime, comment="健康证到期时间")
    emergency_contact = Column(String(100), comment="紧急联系人")
    emergency_phone = Column(String(20), comment="紧急联系电话")
    
    # 工作状态
    status = Column(Enum(CrewStatus), default=CrewStatus.INACTIVE, comment="船员状态")
    current_boat_id = Column(Integer, ForeignKey("boats.id"), comment="当前所在船艇ID")
    hire_date = Column(DateTime, comment="入职时间")
    
    # 评级信息
    rating = Column(Integer, default=0, comment="船员评分（1-5星）")
    review_count = Column(Integer, default=0, comment="评价数量")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="crew_info")
    current_boat = relationship("Boat", back_populates="current_crew_members", foreign_keys=[current_boat_id])
    schedules = relationship("Schedule", back_populates="crew")

    def __repr__(self):
        return f"<CrewInfo(id={self.id}, user_id={self.user_id}, level='{self.license_level}', status='{self.status}')>" 
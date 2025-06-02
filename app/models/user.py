from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import UserRole, UserStatus


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    phone = Column(String(20), unique=True, index=True, comment="手机号")
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    
    # 用户信息
    real_name = Column(String(50), comment="真实姓名")
    avatar = Column(String(255), comment="头像URL")
    gender = Column(String(10), comment="性别")
    birth_date = Column(DateTime, comment="出生日期")
    address = Column(Text, comment="地址")
    
    # 系统字段
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False, comment="用户角色")
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False, comment="用户状态")
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_login_at = Column(DateTime, comment="最后登录时间")
    
    # 关系
    role_applications = relationship("RoleApplication", foreign_keys="RoleApplication.user_id", back_populates="user")
    merchant_info = relationship("Merchant", back_populates="user", uselist=False)
    crew_info = relationship("CrewInfo", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>" 
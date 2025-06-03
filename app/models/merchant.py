from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Merchant(Base):
    """商家详细信息模型"""
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True, comment="商家ID")
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="关联用户ID")
    
    # 商家基础信息
    company_name = Column(String(100), nullable=False, comment="公司名称")
    business_license_no = Column(String(50), unique=True, nullable=False, comment="营业执照号")
    legal_representative = Column(String(50), comment="法定代表人")
    registration_address = Column(Text, comment="注册地址")
    business_address = Column(Text, comment="经营地址")
    
    # 联系信息
    contact_person = Column(String(50), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")
    contact_email = Column(String(100), comment="联系邮箱")
    
    # 认证状态
    is_verified = Column(Boolean, default=False, comment="是否已认证")
    verification_date = Column(DateTime, comment="认证时间")
    
    # 业务状态
    is_active = Column(Boolean, default=True, comment="是否活跃")
    rating = Column(Numeric(3, 2), default=0.0, comment="商家评分")
    total_orders = Column(Integer, default=0, comment="总订单数")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="merchant_info")
    boats = relationship("Boat", back_populates="merchant")
    services = relationship("Service", back_populates="merchant")
    
    def __repr__(self):
        return f"<Merchant(id={self.id}, company_name='{self.company_name}', is_verified={self.is_verified})>" 
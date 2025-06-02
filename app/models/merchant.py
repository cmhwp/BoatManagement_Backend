from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Merchant(Base):
    """商家详细信息模型"""
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True, comment="商家ID")
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="关联用户ID")
    
    # 商家基本信息
    business_name = Column(String(100), nullable=False, comment="商家名称")
    business_type = Column(String(50), comment="经营类型")
    business_scope = Column(Text, comment="经营范围")
    registration_number = Column(String(50), unique=True, comment="工商注册号")
    tax_number = Column(String(50), comment="税务登记号")
    
    # 联系信息
    contact_person = Column(String(50), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")
    contact_email = Column(String(100), comment="联系邮箱")
    business_address = Column(Text, comment="经营地址")
    
    # 经营信息
    established_date = Column(DateTime, comment="成立日期")
    business_hours = Column(String(100), comment="营业时间")
    description = Column(Text, comment="商家简介")
    logo_url = Column(String(255), comment="商家Logo URL")
    cover_images = Column(Text, comment="封面图片URLs，JSON格式")
    
    # 财务信息
    bank_name = Column(String(100), comment="开户银行")
    bank_account = Column(String(50), comment="银行账号")
    account_holder = Column(String(50), comment="账户持有人")
    
    # 评级信息
    rating = Column(Numeric(3, 2), default=0.00, comment="平均评分")
    total_reviews = Column(Integer, default=0, comment="总评价数")
    
    # 状态信息
    is_verified = Column(Boolean, default=False, comment="是否已认证")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="merchant_info")
    boats = relationship("Boat", back_populates="merchant")
    services = relationship("Service", back_populates="merchant")
    agricultural_products = relationship("AgriculturalProduct", back_populates="merchant")
    certificates = relationship("Certificate", back_populates="merchant")
    
    def __repr__(self):
        return f"<Merchant(id={self.id}, business_name='{self.business_name}', user_id={self.user_id})>" 
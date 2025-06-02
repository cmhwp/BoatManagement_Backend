from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Decimal, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class MerchantStatus(enum.Enum):
    """商家状态枚举"""
    PENDING = "pending"  # 待审核
    ACTIVE = "active"  # 正常营业
    SUSPENDED = "suspended"  # 暂停营业
    BANNED = "banned"  # 禁止营业


class BusinessType(enum.Enum):
    """经营类型枚举"""
    TOURISM = "tourism"  # 旅游服务
    AGRICULTURE = "agriculture"  # 农产品销售
    COMPREHENSIVE = "comprehensive"  # 综合经营


class Merchant(Base):
    """商家详细信息表"""
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True, comment="商家ID")
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="关联用户ID")
    
    # 基本信息
    business_name = Column(String(200), nullable=False, comment="商家名称")
    business_license = Column(String(50), unique=True, comment="营业执照号")
    business_type = Column(Enum(BusinessType), nullable=False, comment="经营类型")
    legal_person = Column(String(100), comment="法人代表")
    
    # 联系信息
    contact_phone = Column(String(20), comment="联系电话")
    contact_email = Column(String(100), comment="联系邮箱")
    business_address = Column(Text, comment="经营地址")
    region_id = Column(Integer, ForeignKey("regions.id"), comment="所在地区ID")
    
    # 资质信息
    tax_number = Column(String(50), comment="税务登记号")
    bank_account = Column(String(50), comment="银行账户")
    bank_name = Column(String(100), comment="开户银行")
    
    # 经营信息
    description = Column(Text, comment="商家描述")
    logo = Column(String(255), comment="商家Logo")
    banner_images = Column(Text, comment="横幅图片（JSON格式存储URL列表）")
    business_hours = Column(Text, comment="营业时间（JSON格式）")
    
    # 评级信息
    rating = Column(Decimal(3, 2), default=0.00, comment="评分")
    review_count = Column(Integer, default=0, comment="评价数量")
    
    # 状态信息
    status = Column(Enum(MerchantStatus), default=MerchantStatus.PENDING, comment="商家状态")
    is_featured = Column(Boolean, default=False, comment="是否推荐商家")
    verification_level = Column(Integer, default=0, comment="认证级别")
    
    # 时间戳
    approved_at = Column(DateTime, comment="审核通过时间")
    created_at = Column(DateTime, default=datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="merchant")
    region = relationship("Region", back_populates="merchants")
    boats = relationship("Boat", back_populates="merchant")
    services = relationship("Service", back_populates="merchant")
    agricultural_products = relationship("AgriculturalProduct", back_populates="merchant")
    certificates = relationship("Certificate", back_populates="merchant")

    def __repr__(self):
        return f"<Merchant(id={self.id}, business_name='{self.business_name}', status='{self.status}')>" 
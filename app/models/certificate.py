from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class CertificateType(enum.Enum):
    """证书类型枚举"""
    BUSINESS_LICENSE = "business_license"  # 营业执照
    FOOD_SAFETY = "food_safety"  # 食品安全证书
    NAVIGATION = "navigation"  # 航行许可证
    SAFETY = "safety"  # 安全证书
    QUALITY = "quality"  # 质量认证
    ENVIRONMENTAL = "environmental"  # 环保认证
    OTHER = "other"  # 其他


class CertificateStatus(enum.Enum):
    """证书状态枚举"""
    VALID = "valid"  # 有效
    EXPIRED = "expired"  # 已过期
    REVOKED = "revoked"  # 已撤销
    PENDING = "pending"  # 待审核


class Certificate(Base):
    """资质证书管理表"""
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True, comment="证书ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="商家ID")
    
    # 证书基本信息
    name = Column(String(200), nullable=False, comment="证书名称")
    certificate_type = Column(Enum(CertificateType), nullable=False, comment="证书类型")
    certificate_number = Column(String(100), unique=True, comment="证书编号")
    
    # 颁发信息
    issuing_authority = Column(String(200), comment="颁发机构")
    issued_date = Column(DateTime, comment="颁发日期")
    effective_date = Column(DateTime, comment="生效日期")
    expiry_date = Column(DateTime, comment="到期日期")
    
    # 证书内容
    description = Column(Text, comment="证书描述")
    scope = Column(Text, comment="适用范围")
    
    # 文件信息
    certificate_file_url = Column(String(500), comment="证书文件URL")
    file_name = Column(String(200), comment="文件名称")
    file_size = Column(Integer, comment="文件大小（字节）")
    
    # 状态信息
    status = Column(Enum(CertificateStatus), default=CertificateStatus.PENDING, comment="证书状态")
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    
    # 审核信息
    verified_by = Column(Integer, comment="验证人ID")
    verified_at = Column(DateTime, comment="验证时间")
    verification_notes = Column(Text, comment="验证备注")
    
    # 提醒设置
    reminder_days = Column(Integer, default=30, comment="到期提醒天数")
    last_reminder_sent = Column(DateTime, comment="最后提醒时间")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")
    
    # 关联关系
    merchant = relationship("Merchant", back_populates="certificates")

    def __repr__(self):
        return f"<Certificate(id={self.id}, name='{self.name}', type='{self.certificate_type}', status='{self.status}')>" 
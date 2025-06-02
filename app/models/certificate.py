from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import CertificateType


class Certificate(Base):
    """资质证书管理模型"""
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True, comment="证书ID")
    
    # 关联信息
    owner_id = Column(Integer, comment="持有者ID")
    owner_type = Column(String(20), comment="持有者类型(user/merchant/boat)")
    
    # 证书信息
    certificate_type = Column(SQLEnum(CertificateType), nullable=False, comment="证书类型")
    certificate_no = Column(String(100), unique=True, nullable=False, comment="证书编号")
    certificate_name = Column(String(100), nullable=False, comment="证书名称")
    
    # 颁发信息
    issuing_authority = Column(String(100), comment="颁发机构")
    issue_date = Column(DateTime, comment="颁发日期")
    expiry_date = Column(DateTime, comment="到期日期")
    
    # 证书文件
    file_url = Column(String(255), comment="证书文件URL")
    
    # 验证状态
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    verified_at = Column(DateTime, comment="验证时间")
    verified_by = Column(Integer, ForeignKey("users.id"), comment="验证人ID")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否有效")
    
    # 备注
    notes = Column(Text, comment="备注")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    verifier = relationship("User")
    
    def __repr__(self):
        return f"<Certificate(id={self.id}, type='{self.certificate_type}', no='{self.certificate_no}')>" 
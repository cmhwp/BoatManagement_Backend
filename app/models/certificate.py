from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import CertificateType, CertificateStatus


class Certificate(Base):
    """资质证书管理模型"""
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True, comment="证书ID")
    
    # 关联信息
    merchant_id = Column(Integer, ForeignKey("merchants.id"), comment="商家ID")
    crew_id = Column(Integer, ForeignKey("crew_info.id"), comment="船员ID")
    
    # 证书基本信息
    certificate_type = Column(SQLEnum(CertificateType), nullable=False, comment="证书类型")
    certificate_name = Column(String(100), nullable=False, comment="证书名称")
    certificate_number = Column(String(50), unique=True, comment="证书编号")
    issuing_authority = Column(String(100), comment="颁发机构")
    
    # 时间信息
    issue_date = Column(DateTime, comment="颁发日期")
    expiry_date = Column(DateTime, comment="到期日期")
    renewal_date = Column(DateTime, comment="续期日期")
    
    # 证书状态
    status = Column(SQLEnum(CertificateStatus), default=CertificateStatus.PENDING, comment="证书状态")
    
    # 文件信息
    certificate_file_url = Column(String(255), comment="证书文件URL")
    scan_copy_url = Column(String(255), comment="扫描件URL")
    
    # 审核信息
    reviewer_id = Column(Integer, ForeignKey("users.id"), comment="审核人ID")
    review_notes = Column(Text, comment="审核备注")
    reviewed_at = Column(DateTime, comment="审核时间")
    
    # 提醒信息
    reminder_days = Column(Integer, default=30, comment="到期提醒天数")
    last_reminder_sent = Column(DateTime, comment="最后提醒时间")
    
    # 备注信息
    description = Column(Text, comment="证书描述")
    notes = Column(Text, comment="备注")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    merchant = relationship("Merchant", back_populates="certificates")
    crew = relationship("CrewInfo", back_populates="certificates")
    reviewer = relationship("User")
    
    def __repr__(self):
        return f"<Certificate(id={self.id}, name='{self.certificate_name}', status='{self.status}')>" 
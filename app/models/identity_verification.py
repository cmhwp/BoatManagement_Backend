from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import IdentityType, VerificationStatus


class IdentityVerification(Base):
    """实名认证模型"""
    __tablename__ = "identity_verifications"

    id = Column(Integer, primary_key=True, index=True, comment="认证ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    
    # 身份信息
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    identity_type = Column(SQLEnum(IdentityType), default=IdentityType.ID_CARD, nullable=False, comment="证件类型")
    identity_number = Column(String(30), nullable=False, comment="证件号码")
    
    # 认证材料
    front_image = Column(String(255), comment="证件正面照片URL")
    back_image = Column(String(255), comment="证件背面照片URL")
    
    # 认证状态
    status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False, comment="认证状态")
    reject_reason = Column(Text, comment="拒绝原因")
    verified_at = Column(DateTime, comment="认证通过时间")
    expires_at = Column(DateTime, comment="认证过期时间")
    
    # 审核信息
    reviewer_id = Column(Integer, ForeignKey("users.id"), comment="审核员ID")
    reviewed_at = Column(DateTime, comment="审核时间")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", foreign_keys=[user_id], back_populates="identity_verification")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    
    def __repr__(self):
        return f"<IdentityVerification(id={self.id}, user_id={self.user_id}, status='{self.status}')>" 
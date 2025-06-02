from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import UserRole, ApplicationStatus


class RoleApplication(Base):
    """角色申请记录模型"""
    __tablename__ = "role_applications"

    id = Column(Integer, primary_key=True, index=True, comment="申请ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="申请用户ID")
    current_role = Column(SQLEnum(UserRole), nullable=False, comment="当前角色")
    target_role = Column(SQLEnum(UserRole), nullable=False, comment="目标角色")
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING, comment="申请状态")
    
    # 申请信息
    reason = Column(Text, comment="申请理由")
    business_license = Column(String(255), comment="营业执照文件URL")
    certificates = Column(Text, comment="相关证书文件URLs(JSON格式)")
    contact_info = Column(Text, comment="联系方式")
    
    # 审核信息
    reviewer_id = Column(Integer, ForeignKey("users.id"), comment="审核人ID")
    review_note = Column(Text, comment="审核备注")
    reviewed_at = Column(DateTime, comment="审核时间")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="申请时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", foreign_keys=[user_id], back_populates="role_applications")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    
    def __repr__(self):
        return f"<RoleApplication(id={self.id}, user_id={self.user_id}, target_role='{self.target_role}', status='{self.status}')>" 
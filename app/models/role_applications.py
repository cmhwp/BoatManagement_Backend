from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class TargetRole(str, enum.Enum):
    merchant = "merchant"
    crew = "crew"


class ApplicationStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class RoleApplication(Base):
    __tablename__ = "role_applications"

    application_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    target_role = Column(Enum(TargetRole), nullable=False)
    application_data = Column(JSON, nullable=False)  # 资质文件路径等
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.pending)
    applied_time = Column(DateTime, default=func.now())
    reviewed_time = Column(DateTime)
    review_notes = Column(Text)

    # 关系
    user = relationship("User", back_populates="role_applications") 
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class UserRole(str, enum.Enum):
    user = "user"
    merchant = "merchant"
    crew = "crew"
    pending_merchant = "pending_merchant"
    pending_crew = "pending_crew"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, index=True)
    role = Column(Enum(UserRole), default=UserRole.user)
    create_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)
    update_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_delete = Column(Boolean, default=False)

    # 关系
    role_applications = relationship("RoleApplication", back_populates="user")
    merchant = relationship("Merchant", back_populates="user", uselist=False)
    crew_info = relationship("CrewInfo", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user") 
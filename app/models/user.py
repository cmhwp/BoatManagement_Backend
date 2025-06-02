from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class UserRole(enum.Enum):
    """用户角色枚举"""
    TOURIST = "tourist"  # 游客
    MERCHANT = "merchant"  # 商家
    CREW = "crew"  # 船员
    ADMIN = "admin"  # 管理员


class UserStatus(enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"  # 激活
    INACTIVE = "inactive"  # 未激活
    BANNED = "banned"  # 封禁


class RoleApplicationStatus(enum.Enum):
    """角色申请状态枚举"""
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝


class User(Base):
    """用户基础信息表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    phone = Column(String(20), unique=True, index=True, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    
    # 基本信息
    real_name = Column(String(100), comment="真实姓名")
    avatar = Column(String(255), comment="头像URL")
    gender = Column(Enum("male", "female", "other"), comment="性别")
    birthday = Column(DateTime, comment="生日")
    id_card = Column(String(18), comment="身份证号")
    
    # 联系信息
    address = Column(Text, comment="地址")
    region_id = Column(Integer, ForeignKey("regions.id"), comment="所属地区ID")
    
    # 系统信息
    role = Column(Enum(UserRole), default=UserRole.TOURIST, comment="用户角色")
    status = Column(Enum(UserStatus), default=UserStatus.INACTIVE, comment="用户状态")
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")
    last_login = Column(DateTime, comment="最后登录时间")
    
    # 关联关系
    region = relationship("Region", back_populates="users")
    role_applications = relationship("RoleApplication", back_populates="user")
    merchant = relationship("Merchant", back_populates="user", uselist=False)
    crew_info = relationship("CrewInfo", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    user_coupons = relationship("UserCoupon", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class RoleApplication(Base):
    """角色申请记录表"""
    __tablename__ = "role_applications"

    id = Column(Integer, primary_key=True, index=True, comment="申请ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    target_role = Column(Enum(UserRole), nullable=False, comment="申请角色")
    
    # 申请信息
    application_reason = Column(Text, comment="申请理由")
    supporting_documents = Column(Text, comment="支持文档（JSON格式存储文件URL列表）")
    
    # 审核信息
    status = Column(Enum(RoleApplicationStatus), default=RoleApplicationStatus.PENDING, comment="申请状态")
    reviewer_id = Column(Integer, ForeignKey("users.id"), comment="审核人ID")
    review_comment = Column(Text, comment="审核意见")
    reviewed_at = Column(DateTime, comment="审核时间")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now(), comment="申请时间")
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="role_applications", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])

    def __repr__(self):
        return f"<RoleApplication(id={self.id}, user_id={self.user_id}, target_role='{self.target_role}', status='{self.status}')>" 
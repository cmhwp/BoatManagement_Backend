from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class NotificationType(enum.Enum):
    """通知类型枚举"""
    SYSTEM = "system"  # 系统通知
    ORDER = "order"  # 订单通知
    PAYMENT = "payment"  # 支付通知
    PROMOTION = "promotion"  # 促销通知
    SECURITY = "security"  # 安全通知
    REMINDER = "reminder"  # 提醒通知


class NotificationPriority(enum.Enum):
    """通知优先级枚举"""
    LOW = "low"  # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"  # 高
    URGENT = "urgent"  # 紧急


class NotificationStatus(enum.Enum):
    """通知状态枚举"""
    UNREAD = "unread"  # 未读
    READ = "read"  # 已读
    ARCHIVED = "archived"  # 已归档


class Notification(Base):
    """系统消息通知表"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, comment="通知ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="接收用户ID")
    
    # 通知基本信息
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=False, comment="通知内容")
    notification_type = Column(Enum(NotificationType), nullable=False, comment="通知类型")
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM, comment="优先级")
    
    # 关联信息
    related_id = Column(Integer, comment="关联对象ID（如订单ID、支付ID等）")
    related_type = Column(String(50), comment="关联对象类型")
    
    # 状态信息
    status = Column(Enum(NotificationStatus), default=NotificationStatus.UNREAD, comment="通知状态")
    is_push = Column(Boolean, default=False, comment="是否推送")
    is_email = Column(Boolean, default=False, comment="是否发送邮件")
    is_sms = Column(Boolean, default=False, comment="是否发送短信")
    
    # 操作信息
    action_url = Column(String(500), comment="操作链接")
    action_text = Column(String(100), comment="操作按钮文本")
    
    # 发送状态
    push_sent = Column(Boolean, default=False, comment="推送是否已发送")
    email_sent = Column(Boolean, default=False, comment="邮件是否已发送")
    sms_sent = Column(Boolean, default=False, comment="短信是否已发送")
    
    # 时间信息
    scheduled_at = Column(DateTime, comment="计划发送时间")
    sent_at = Column(DateTime, comment="实际发送时间")
    read_at = Column(DateTime, comment="阅读时间")
    expires_at = Column(DateTime, comment="过期时间")
    
    # 额外数据
    extra_data = Column(Text, comment="额外数据（JSON格式）")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.notification_type}', status='{self.status}')>" 
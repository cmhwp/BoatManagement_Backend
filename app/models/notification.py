from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import NotificationType


class Notification(Base):
    """系统消息通知模型"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, comment="通知ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="接收用户ID")
    
    # 通知内容
    title = Column(String(100), nullable=False, comment="通知标题")
    content = Column(Text, nullable=False, comment="通知内容")
    notification_type = Column(SQLEnum(NotificationType), nullable=False, comment="通知类型")
    
    # 关联信息
    related_id = Column(Integer, comment="关联业务ID")
    related_type = Column(String(50), comment="关联业务类型")
    
    # 状态信息
    is_read = Column(Boolean, default=False, comment="是否已读")
    read_at = Column(DateTime, comment="阅读时间")
    
    # 推送信息
    is_pushed = Column(Boolean, default=False, comment="是否已推送")
    push_channel = Column(String(50), comment="推送渠道")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系
    user = relationship("User")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.notification_type}', is_read={self.is_read})>" 
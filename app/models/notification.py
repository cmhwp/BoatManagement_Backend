from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import NotificationType, NotificationStatus


class Notification(Base):
    """系统消息通知模型"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, comment="通知ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="接收用户ID")
    
    # 通知基本信息
    notification_type = Column(SQLEnum(NotificationType), nullable=False, comment="通知类型")
    title = Column(String(100), nullable=False, comment="通知标题")
    content = Column(Text, nullable=False, comment="通知内容")
    
    # 关联信息
    order_id = Column(Integer, ForeignKey("orders.id"), comment="关联订单ID")
    payment_id = Column(Integer, ForeignKey("payments.id"), comment="关联支付ID")
    
    # 状态信息
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.UNREAD, comment="通知状态")
    priority = Column(String(10), default="normal", comment="优先级（low/normal/high/urgent）")
    
    # 发送信息
    sender_id = Column(Integer, ForeignKey("users.id"), comment="发送者ID")
    send_method = Column(String(20), comment="发送方式（app/sms/email）")
    
    # 额外数据
    extra_data = Column(Text, comment="额外数据，JSON格式")
    action_url = Column(String(255), comment="操作链接")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    read_at = Column(DateTime, comment="阅读时间")
    archived_at = Column(DateTime, comment="归档时间")
    
    # 关系
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    sender = relationship("User", foreign_keys=[sender_id])
    order = relationship("Order")
    payment = relationship("Payment")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.notification_type}', status='{self.status}')>" 
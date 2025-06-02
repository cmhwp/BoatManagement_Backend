from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """通知类型枚举"""
    SYSTEM = "system"                 # 系统通知
    ORDER = "order"                   # 订单通知
    PAYMENT = "payment"               # 支付通知
    REVIEW = "review"                 # 评价通知
    MERCHANT = "merchant"             # 商家通知
    PRODUCT = "product"               # 产品通知
    PROMOTION = "promotion"           # 促销通知
    INVENTORY = "inventory"           # 库存预警
    REMINDER = "reminder"             # 提醒通知
    ANNOUNCEMENT = "announcement"     # 公告通知


class NotificationStatus(str, Enum):
    """通知状态枚举"""
    UNREAD = "unread"                # 未读
    READ = "read"                    # 已读
    DELETED = "deleted"              # 已删除
    ARCHIVED = "archived"            # 已归档


class NotificationChannel(str, Enum):
    """通知渠道枚举"""
    IN_APP = "in_app"                # 站内信
    EMAIL = "email"                  # 邮件
    SMS = "sms"                      # 短信
    PUSH = "push"                    # 推送通知
    WECHAT = "wechat"                # 微信


class NotificationPriority(str, Enum):
    """通知优先级枚举"""
    LOW = "low"                      # 低优先级
    NORMAL = "normal"                # 普通优先级
    HIGH = "high"                    # 高优先级
    URGENT = "urgent"                # 紧急


# 通知创建模型
class NotificationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="通知标题")
    content: str = Field(..., min_length=1, max_length=2000, description="通知内容")
    notification_type: NotificationType = Field(..., description="通知类型")
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL, description="优先级")
    channels: List[NotificationChannel] = Field(default=[NotificationChannel.IN_APP], description="通知渠道")
    recipient_ids: Optional[List[int]] = Field(None, description="接收者用户ID列表")
    recipient_roles: Optional[List[str]] = Field(None, description="接收者角色列表")
    recipient_all: bool = Field(default=False, description="是否发送给所有用户")
    related_id: Optional[int] = Field(None, description="关联对象ID")
    related_type: Optional[str] = Field(None, max_length=50, description="关联对象类型")
    action_url: Optional[str] = Field(None, max_length=500, description="操作链接")
    action_text: Optional[str] = Field(None, max_length=50, description="操作按钮文本")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外数据")
    scheduled_at: Optional[datetime] = Field(None, description="计划发送时间")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    
    @validator('recipient_ids')
    def validate_recipients(cls, v, values):
        recipient_all = values.get('recipient_all', False)
        recipient_roles = values.get('recipient_roles')
        
        if not recipient_all and not v and not recipient_roles:
            raise ValueError('必须指定接收者：用户ID列表、角色列表或全部用户')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1, max_length=2000)
    priority: Optional[NotificationPriority] = None
    action_url: Optional[str] = Field(None, max_length=500)
    action_text: Optional[str] = Field(None, max_length=50)
    extra_data: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class NotificationResponse(BaseModel):
    id: int
    title: str
    content: str
    notification_type: NotificationType
    priority: NotificationPriority
    channels: List[NotificationChannel]
    related_id: Optional[int]
    related_type: Optional[str]
    action_url: Optional[str]
    action_text: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    sender_id: Optional[int]
    created_at: datetime
    scheduled_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    # 关联信息
    sender: Optional[Dict[str, Any]] = None
    recipients_count: int = 0
    read_count: int = 0
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class NotificationListResponse(BaseModel):
    id: int
    title: str
    notification_type: NotificationType
    priority: NotificationPriority
    channels: List[NotificationChannel]
    created_at: datetime
    recipients_count: int
    read_count: int
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# 用户通知模型
class UserNotificationResponse(BaseModel):
    id: int
    notification_id: int
    status: NotificationStatus
    read_at: Optional[datetime]
    created_at: datetime
    
    # 通知信息
    notification: Dict[str, Any]
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class UserNotificationUpdate(BaseModel):
    status: NotificationStatus
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# 通知模板模型
class NotificationTemplate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    template_type: NotificationType = Field(..., description="模板类型")
    title_template: str = Field(..., min_length=1, max_length=200, description="标题模板")
    content_template: str = Field(..., min_length=1, max_length=2000, description="内容模板")
    channels: List[NotificationChannel] = Field(default=[NotificationChannel.IN_APP], description="默认渠道")
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL, description="默认优先级")
    variables: List[str] = Field(default_factory=list, description="模板变量列表")
    is_active: bool = Field(default=True, description="是否启用")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# 通知搜索筛选模型
class NotificationSearchFilter(BaseModel):
    notification_type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    status: Optional[NotificationStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    keyword: Optional[str] = Field(None, max_length=100, description="搜索关键词")
    sender_id: Optional[int] = None
    related_type: Optional[str] = None
    related_id: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# 通知统计模型
class NotificationStatistics(BaseModel):
    total_notifications: int = Field(default=0, description="通知总数")
    unread_count: int = Field(default=0, description="未读数量")
    read_count: int = Field(default=0, description="已读数量")
    type_distribution: Dict[str, int] = Field(default_factory=dict, description="类型分布")
    priority_distribution: Dict[str, int] = Field(default_factory=dict, description="优先级分布")
    channel_distribution: Dict[str, int] = Field(default_factory=dict, description="渠道分布")
    daily_counts: List[Dict[str, Any]] = Field(default_factory=list, description="每日通知数量")
    read_rate: float = Field(default=0.0, description="阅读率")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# 批量操作模型
class BulkNotificationOperation(BaseModel):
    notification_ids: List[int] = Field(..., min_items=1, description="通知ID列表")
    operation: str = Field(..., description="操作类型")
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['mark_read', 'mark_unread', 'delete', 'archive']
        if v not in allowed_operations:
            raise ValueError(f'操作类型必须是: {", ".join(allowed_operations)}')
        return v


# 通知设置模型
class NotificationSettings(BaseModel):
    user_id: int
    email_enabled: bool = Field(default=True, description="邮件通知开启")
    sms_enabled: bool = Field(default=False, description="短信通知开启")
    push_enabled: bool = Field(default=True, description="推送通知开启")
    wechat_enabled: bool = Field(default=False, description="微信通知开启")
    order_notifications: bool = Field(default=True, description="订单通知")
    payment_notifications: bool = Field(default=True, description="支付通知")
    review_notifications: bool = Field(default=True, description="评价通知")
    merchant_notifications: bool = Field(default=True, description="商家通知")
    promotion_notifications: bool = Field(default=True, description="促销通知")
    system_notifications: bool = Field(default=True, description="系统通知")
    quiet_hours_start: Optional[str] = Field(None, description="免打扰开始时间")
    quiet_hours_end: Optional[str] = Field(None, description="免打扰结束时间")
    
    class Config:
        from_attributes = True


class NotificationSettingsUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    wechat_enabled: Optional[bool] = None
    order_notifications: Optional[bool] = None
    payment_notifications: Optional[bool] = None
    review_notifications: Optional[bool] = None
    merchant_notifications: Optional[bool] = None
    promotion_notifications: Optional[bool] = None
    system_notifications: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None 
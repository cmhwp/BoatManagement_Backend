from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from datetime import datetime, timedelta
import json

from app.crud.base import CRUDBase
from app.models.notification import Notification, UserNotification, NotificationSettings
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, UserNotificationUpdate,
    NotificationSearchFilter, NotificationType, NotificationStatus,
    NotificationPriority, NotificationChannel, NotificationSettingsUpdate
)


class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):
    """通知CRUD操作类"""
    
    def create_with_recipients(
        self, 
        db: Session, 
        *, 
        obj_in: NotificationCreate,
        sender_id: Optional[int] = None
    ) -> Notification:
        """创建通知并添加接收者"""
        from app.crud.user import crud_user
        
        # 处理通知数据
        notification_data = obj_in.model_dump(exclude={'recipient_ids', 'recipient_roles', 'recipient_all'})
        notification_data["sender_id"] = sender_id
        notification_data["channels"] = json.dumps([channel.value for channel in obj_in.channels], ensure_ascii=False)
        
        if obj_in.extra_data:
            notification_data["extra_data"] = json.dumps(obj_in.extra_data, ensure_ascii=False)
        
        # 创建通知
        notification = self.create(db, obj_in=notification_data)
        
        # 获取接收者列表
        recipient_ids = []
        
        if obj_in.recipient_all:
            # 发送给所有用户
            all_users = crud_user.get_multi(db, skip=0, limit=10000)
            recipient_ids = [user.id for user in all_users]
        elif obj_in.recipient_roles:
            # 发送给指定角色的用户
            for role in obj_in.recipient_roles:
                role_users = crud_user.get_by_role(db, role=role)
                recipient_ids.extend([user.id for user in role_users])
        elif obj_in.recipient_ids:
            # 发送给指定用户
            recipient_ids = obj_in.recipient_ids
        
        # 去重
        recipient_ids = list(set(recipient_ids))
        
        # 创建用户通知记录
        crud_user_notification = CRUDUserNotification(UserNotification)
        for recipient_id in recipient_ids:
            user_notification_data = {
                "notification_id": notification.id,
                "user_id": recipient_id,
                "status": NotificationStatus.UNREAD
            }
            crud_user_notification.create(db, obj_in=user_notification_data)
        
        return notification
    
    def get_by_sender_id(
        self, 
        db: Session, 
        *, 
        sender_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """获取发送者的通知列表"""
        return (
            db.query(Notification)
            .filter(Notification.sender_id == sender_id)
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_type(
        self, 
        db: Session, 
        *, 
        notification_type: NotificationType, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """根据类型获取通知"""
        return (
            db.query(Notification)
            .filter(Notification.notification_type == notification_type)
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_notifications(
        self,
        db: Session,
        *,
        filter_params: NotificationSearchFilter,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        """搜索通知"""
        query = db.query(Notification)
        
        # 类型筛选
        if filter_params.notification_type:
            query = query.filter(Notification.notification_type == filter_params.notification_type)
        
        # 优先级筛选
        if filter_params.priority:
            query = query.filter(Notification.priority == filter_params.priority)
        
        # 发送者筛选
        if filter_params.sender_id:
            query = query.filter(Notification.sender_id == filter_params.sender_id)
        
        # 关联对象筛选
        if filter_params.related_type:
            query = query.filter(Notification.related_type == filter_params.related_type)
        
        if filter_params.related_id:
            query = query.filter(Notification.related_id == filter_params.related_id)
        
        # 时间范围筛选
        if filter_params.start_date:
            query = query.filter(Notification.created_at >= filter_params.start_date)
        if filter_params.end_date:
            query = query.filter(Notification.created_at <= filter_params.end_date)
        
        # 关键词搜索
        if filter_params.keyword:
            keyword = f"%{filter_params.keyword}%"
            query = query.filter(
                or_(
                    Notification.title.like(keyword),
                    Notification.content.like(keyword)
                )
            )
        
        return (
            query
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_scheduled_notifications(self, db: Session) -> List[Notification]:
        """获取计划发送的通知"""
        now = datetime.now()
        return (
            db.query(Notification)
            .filter(
                and_(
                    Notification.scheduled_at <= now,
                    Notification.scheduled_at.isnot(None)
                )
            )
            .all()
        )
    
    def get_expired_notifications(self, db: Session) -> List[Notification]:
        """获取已过期的通知"""
        now = datetime.now()
        return (
            db.query(Notification)
            .filter(
                and_(
                    Notification.expires_at <= now,
                    Notification.expires_at.isnot(None)
                )
            )
            .all()
        )
    
    def get_notification_statistics(
        self, 
        db: Session, 
        *, 
        sender_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取通知统计信息"""
        query = db.query(Notification)
        
        if sender_id:
            query = query.filter(Notification.sender_id == sender_id)
        
        if start_date:
            query = query.filter(Notification.created_at >= start_date)
        if end_date:
            query = query.filter(Notification.created_at <= end_date)
        
        notifications = query.all()
        
        if not notifications:
            return {
                "total_notifications": 0,
                "type_distribution": {},
                "priority_distribution": {},
                "channel_distribution": {},
                "daily_counts": []
            }
        
        total_notifications = len(notifications)
        
        # 类型分布
        type_distribution = {}
        for notification in notifications:
            ntype = notification.notification_type
            type_distribution[ntype] = type_distribution.get(ntype, 0) + 1
        
        # 优先级分布
        priority_distribution = {}
        for notification in notifications:
            priority = notification.priority
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        # 渠道分布
        channel_distribution = {}
        for notification in notifications:
            channels = json.loads(notification.channels) if notification.channels else []
            for channel in channels:
                channel_distribution[channel] = channel_distribution.get(channel, 0) + 1
        
        # 每日统计
        daily_counts = self._get_daily_notification_counts(db, notifications, start_date, end_date)
        
        return {
            "total_notifications": total_notifications,
            "type_distribution": type_distribution,
            "priority_distribution": priority_distribution,
            "channel_distribution": channel_distribution,
            "daily_counts": daily_counts
        }
    
    def _get_daily_notification_counts(
        self, 
        db: Session, 
        notifications: List[Notification],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """获取每日通知数量统计"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # 按日期分组统计
        daily_counts = {}
        for notification in notifications:
            date_key = notification.created_at.date().isoformat()
            if date_key not in daily_counts:
                daily_counts[date_key] = 0
            daily_counts[date_key] += 1
        
        # 创建完整的日期序列
        result = []
        current_date = start_date.date()
        end_date = end_date.date()
        
        while current_date <= end_date:
            date_key = current_date.isoformat()
            result.append({
                "date": date_key,
                "count": daily_counts.get(date_key, 0)
            })
            current_date += timedelta(days=1)
        
        return result
    
    def get_recipients_count(self, db: Session, *, notification_id: int) -> int:
        """获取通知接收者数量"""
        return (
            db.query(UserNotification)
            .filter(UserNotification.notification_id == notification_id)
            .count()
        )
    
    def get_read_count(self, db: Session, *, notification_id: int) -> int:
        """获取通知已读数量"""
        return (
            db.query(UserNotification)
            .filter(
                and_(
                    UserNotification.notification_id == notification_id,
                    UserNotification.status == NotificationStatus.READ
                )
            )
            .count()
        )


class CRUDUserNotification(CRUDBase[UserNotification, dict, UserNotificationUpdate]):
    """用户通知CRUD操作类"""
    
    def get_user_notifications(
        self, 
        db: Session, 
        *, 
        user_id: int,
        status: Optional[NotificationStatus] = None,
        notification_type: Optional[NotificationType] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[UserNotification]:
        """获取用户通知列表"""
        query = (
            db.query(UserNotification)
            .filter(UserNotification.user_id == user_id)
            .join(Notification)
        )
        
        if status:
            query = query.filter(UserNotification.status == status)
        
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)
        
        return (
            query
            .order_by(desc(UserNotification.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_unread_count(self, db: Session, *, user_id: int) -> int:
        """获取用户未读通知数量"""
        return (
            db.query(UserNotification)
            .filter(
                and_(
                    UserNotification.user_id == user_id,
                    UserNotification.status == NotificationStatus.UNREAD
                )
            )
            .count()
        )
    
    def mark_as_read(self, db: Session, *, user_id: int, notification_id: int) -> Optional[UserNotification]:
        """标记通知为已读"""
        user_notification = (
            db.query(UserNotification)
            .filter(
                and_(
                    UserNotification.user_id == user_id,
                    UserNotification.notification_id == notification_id
                )
            )
            .first()
        )
        
        if user_notification and user_notification.status == NotificationStatus.UNREAD:
            return self.update(
                db,
                db_obj=user_notification,
                obj_in={"status": NotificationStatus.READ, "read_at": datetime.now()}
            )
        
        return user_notification
    
    def mark_all_as_read(self, db: Session, *, user_id: int) -> int:
        """标记用户所有通知为已读"""
        updated_count = (
            db.query(UserNotification)
            .filter(
                and_(
                    UserNotification.user_id == user_id,
                    UserNotification.status == NotificationStatus.UNREAD
                )
            )
            .update({
                "status": NotificationStatus.READ,
                "read_at": datetime.now()
            })
        )
        db.commit()
        return updated_count
    
    def delete_user_notification(self, db: Session, *, user_id: int, notification_id: int) -> bool:
        """删除用户通知"""
        user_notification = (
            db.query(UserNotification)
            .filter(
                and_(
                    UserNotification.user_id == user_id,
                    UserNotification.notification_id == notification_id
                )
            )
            .first()
        )
        
        if user_notification:
            self.update(
                db,
                db_obj=user_notification,
                obj_in={"status": NotificationStatus.DELETED}
            )
            return True
        
        return False
    
    def bulk_update_status(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        notification_ids: List[int], 
        status: NotificationStatus
    ) -> int:
        """批量更新通知状态"""
        update_data = {"status": status}
        if status == NotificationStatus.READ:
            update_data["read_at"] = datetime.now()
        
        updated_count = (
            db.query(UserNotification)
            .filter(
                and_(
                    UserNotification.user_id == user_id,
                    UserNotification.notification_id.in_(notification_ids)
                )
            )
            .update(update_data)
        )
        db.commit()
        return updated_count
    
    def get_user_notification_statistics(
        self, 
        db: Session, 
        *, 
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取用户通知统计"""
        query = (
            db.query(UserNotification)
            .filter(UserNotification.user_id == user_id)
            .join(Notification)
        )
        
        if start_date:
            query = query.filter(UserNotification.created_at >= start_date)
        if end_date:
            query = query.filter(UserNotification.created_at <= end_date)
        
        user_notifications = query.all()
        
        if not user_notifications:
            return {
                "total_notifications": 0,
                "unread_count": 0,
                "read_count": 0,
                "read_rate": 0.0,
                "type_distribution": {}
            }
        
        total_notifications = len(user_notifications)
        unread_count = len([un for un in user_notifications if un.status == NotificationStatus.UNREAD])
        read_count = len([un for un in user_notifications if un.status == NotificationStatus.READ])
        read_rate = (read_count / total_notifications) * 100 if total_notifications > 0 else 0
        
        # 类型分布
        type_distribution = {}
        for user_notification in user_notifications:
            ntype = user_notification.notification.notification_type
            type_distribution[ntype] = type_distribution.get(ntype, 0) + 1
        
        return {
            "total_notifications": total_notifications,
            "unread_count": unread_count,
            "read_count": read_count,
            "read_rate": round(read_rate, 2),
            "type_distribution": type_distribution
        }


class CRUDNotificationSettings(CRUDBase[NotificationSettings, dict, NotificationSettingsUpdate]):
    """通知设置CRUD操作类"""
    
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[NotificationSettings]:
        """根据用户ID获取通知设置"""
        return db.query(NotificationSettings).filter(NotificationSettings.user_id == user_id).first()
    
    def create_default_settings(self, db: Session, *, user_id: int) -> NotificationSettings:
        """为用户创建默认通知设置"""
        settings_data = {"user_id": user_id}
        return self.create(db, obj_in=settings_data)
    
    def get_or_create_settings(self, db: Session, *, user_id: int) -> NotificationSettings:
        """获取或创建用户通知设置"""
        settings = self.get_by_user_id(db, user_id=user_id)
        if not settings:
            settings = self.create_default_settings(db, user_id=user_id)
        return settings
    
    def is_notification_enabled(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        notification_type: NotificationType,
        channel: NotificationChannel
    ) -> bool:
        """检查用户是否启用了指定类型和渠道的通知"""
        settings = self.get_by_user_id(db, user_id=user_id)
        if not settings:
            return True  # 默认启用
        
        # 检查渠道是否启用
        channel_enabled = True
        if channel == NotificationChannel.EMAIL:
            channel_enabled = settings.email_enabled
        elif channel == NotificationChannel.SMS:
            channel_enabled = settings.sms_enabled
        elif channel == NotificationChannel.PUSH:
            channel_enabled = settings.push_enabled
        elif channel == NotificationChannel.WECHAT:
            channel_enabled = settings.wechat_enabled
        
        if not channel_enabled:
            return False
        
        # 检查通知类型是否启用
        type_enabled = True
        if notification_type == NotificationType.ORDER:
            type_enabled = settings.order_notifications
        elif notification_type == NotificationType.PAYMENT:
            type_enabled = settings.payment_notifications
        elif notification_type == NotificationType.REVIEW:
            type_enabled = settings.review_notifications
        elif notification_type == NotificationType.MERCHANT:
            type_enabled = settings.merchant_notifications
        elif notification_type == NotificationType.PROMOTION:
            type_enabled = settings.promotion_notifications
        elif notification_type == NotificationType.SYSTEM:
            type_enabled = settings.system_notifications
        
        return type_enabled


# 创建CRUD实例
crud_notification = CRUDNotification(Notification)
crud_user_notification = CRUDUserNotification(UserNotification)
crud_notification_settings = CRUDNotificationSettings(NotificationSettings) 
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationSearchFilter, UserNotificationUpdate, NotificationStatistics,
    BulkNotificationOperation, NotificationSettings, NotificationSettingsUpdate,
    NotificationType, NotificationStatus, NotificationPriority
)
from app.services.notification_service import NotificationService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.dependencies import get_current_user, require_admin

router = APIRouter()


@router.post("", summary="创建通知")
async def create_notification(
    notification_create: NotificationCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建通知（管理员和商家）"""
    try:
        result = NotificationService.create_notification(db, current_user.id, notification_create)
        return success_response(
            message="通知创建成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/my-notifications", summary="获取我的通知")
async def get_my_notifications(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[NotificationStatus] = Query(None, description="通知状态"),
    notification_type: Optional[NotificationType] = Query(None, description="通知类型"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户通知列表"""
    try:
        skip = (page - 1) * size
        result = NotificationService.get_user_notifications(
            db=db,
            user_id=current_user.id,
            status=status,
            notification_type=notification_type,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["notifications"],
            total=result["total"],
            page=page,
            size=size,
            message="获取通知列表成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/admin/notifications", summary="管理员获取所有通知")
async def get_admin_notifications(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    notification_type: Optional[NotificationType] = Query(None, description="通知类型"),
    priority: Optional[NotificationPriority] = Query(None, description="优先级"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    sender_id: Optional[int] = Query(None, description="发送者ID"),
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员获取所有通知列表"""
    try:
        skip = (page - 1) * size
        
        filter_params = NotificationSearchFilter(
            notification_type=notification_type,
            priority=priority,
            keyword=keyword,
            sender_id=sender_id
        )
        
        result = NotificationService.get_admin_notifications(
            db=db,
            user_id=current_user.id,
            filter_params=filter_params,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["notifications"],
            total=result["total"],
            page=page,
            size=size,
            message="获取通知列表成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/unread-count", summary="获取未读通知数量")
async def get_unread_count(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户未读通知数量"""
    try:
        result = NotificationService.get_unread_count(db, current_user.id)
        return success_response(
            message="获取未读通知数量成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/statistics", summary="获取通知统计")
async def get_notification_statistics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取通知统计信息"""
    try:
        result = NotificationService.get_notification_statistics(db, current_user.id)
        return success_response(
            message="获取通知统计成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/{notification_id}", summary="获取通知详情")
async def get_notification_detail(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取通知详细信息"""
    try:
        result = NotificationService.get_notification_detail(db, current_user.id, notification_id)
        return success_response(
            message="获取通知详情成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.put("/{notification_id}", summary="更新通知")
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新通知信息"""
    try:
        result = NotificationService.update_notification(
            db, current_user.id, notification_id, notification_update
        )
        return success_response(
            message="通知更新成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.delete("/{notification_id}", summary="删除通知")
async def delete_notification(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除通知"""
    try:
        result = NotificationService.delete_notification(db, current_user.id, notification_id)
        return success_response(
            message="通知删除成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.patch("/{notification_id}/read", summary="标记通知为已读")
async def mark_notification_as_read(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记指定通知为已读"""
    try:
        result = NotificationService.mark_notification_as_read(
            db, current_user.id, notification_id
        )
        return success_response(
            message="通知已标记为已读",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.patch("/mark-all-read", summary="标记所有通知为已读")
async def mark_all_notifications_as_read(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记所有通知为已读"""
    try:
        result = NotificationService.mark_all_as_read(db, current_user.id)
        return success_response(
            message="所有通知已标记为已读",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.delete("/{notification_id}/user", summary="删除用户通知")
async def delete_user_notification(
    notification_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除用户通知"""
    try:
        result = NotificationService.delete_user_notification(
            db, current_user.id, notification_id
        )
        return success_response(
            message="通知删除成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/bulk-operations", summary="批量操作通知")
async def bulk_update_notifications(
    bulk_operation: BulkNotificationOperation,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量操作通知（标记已读、删除等）"""
    try:
        result = NotificationService.bulk_update_notifications(
            db, current_user.id, bulk_operation
        )
        return success_response(
            message="批量操作成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


# 通知设置接口
@router.get("/settings/my-settings", summary="获取我的通知设置")
async def get_my_notification_settings(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户通知设置"""
    try:
        result = NotificationService.get_notification_settings(db, current_user.id)
        return success_response(
            message="获取通知设置成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.put("/settings/my-settings", summary="更新我的通知设置")
async def update_my_notification_settings(
    settings_update: NotificationSettingsUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户通知设置"""
    try:
        result = NotificationService.update_notification_settings(
            db, current_user.id, settings_update
        )
        return success_response(
            message="通知设置更新成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code) 
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from app.config.database import get_db
from app.utils.deps import require_admin
from app.models.user import User
from app.models.enums import UserRole, UserStatus
from app.schemas.user import UserResponse, UserUpdate, UserCreate
from app.schemas.common import PaginatedResponse, PaginationParams, ApiResponse, MessageResponse
from app.crud.user import get_users, get_user_by_id, update_user, create_user, delete_user
from app.crud.merchant import get_merchants
from app.crud.crew import get_crews
from app.crud.boat import get_boats

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/dashboard", response_model=ApiResponse[Dict[str, Any]])
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取管理员仪表板数据"""
    # 获取用户统计
    user_pagination = PaginationParams(page=1, page_size=1)
    _, total_users = get_users(db, user_pagination)
    
    # 获取商家统计
    merchant_pagination = PaginationParams(page=1, page_size=1)
    _, total_merchants = get_merchants(db, merchant_pagination)
    _, verified_merchants = get_merchants(db, merchant_pagination, is_verified=True)
    
    # 获取船员统计
    crew_pagination = PaginationParams(page=1, page_size=1)
    _, total_crews = get_crews(db, crew_pagination)
    _, available_crews = get_crews(db, crew_pagination, is_available=True)
    
    # 获取船艇统计
    boat_pagination = PaginationParams(page=1, page_size=1)
    _, total_boats = get_boats(db, boat_pagination)
    _, available_boats = get_boats(db, boat_pagination, is_available=True)
    
    # 获取最近30天注册用户数
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_users_pagination = PaginationParams(page=1, page_size=1)
    # 这里需要扩展get_users函数来支持日期过滤，暂时用总数代替
    recent_users = 0  # TODO: 实现日期过滤查询
    
    dashboard_data = {
        "user_stats": {
            "total_users": total_users,
            "recent_users": recent_users,
            "active_users": total_users  # TODO: 实现活跃用户统计
        },
        "merchant_stats": {
            "total_merchants": total_merchants,
            "verified_merchants": verified_merchants,
            "verification_rate": round(verified_merchants / total_merchants * 100, 2) if total_merchants > 0 else 0
        },
        "crew_stats": {
            "total_crews": total_crews,
            "available_crews": available_crews,
            "availability_rate": round(available_crews / total_crews * 100, 2) if total_crews > 0 else 0
        },
        "boat_stats": {
            "total_boats": total_boats,
            "available_boats": available_boats,
            "availability_rate": round(available_boats / total_boats * 100, 2) if total_boats > 0 else 0
        }
    }
    
    return ApiResponse.success_response(data=dashboard_data)


@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_all_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    role: Optional[UserRole] = Query(None, description="用户角色"),
    status: Optional[UserStatus] = Query(None, description="用户状态"),
    is_verified: Optional[bool] = Query(None, description="是否已验证"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取所有用户列表（管理员）"""
    pagination = PaginationParams(page=page, page_size=page_size)
    users, total = get_users(
        db, pagination, role=role, status=status,
        is_verified=is_verified, search=search
    )
    
    return PaginatedResponse.create(
        items=users, total=total, page=page, page_size=page_size
    )


@router.post("/users", response_model=ApiResponse[UserResponse])
async def create_new_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """创建新用户（管理员）"""
    try:
        new_user = create_user(db, user_create)
        return ApiResponse.success_response(
            data=new_user, 
            message="用户创建成功"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/users/{user_id}", response_model=ApiResponse[UserResponse])
async def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取用户详情（管理员）"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return ApiResponse.success_response(data=user)


@router.put("/users/{user_id}", response_model=ApiResponse[UserResponse])
async def update_user_info(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新用户信息（管理员）"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    updated_user = update_user(db, user_id, user_update)
    return ApiResponse.success_response(data=updated_user, message="用户信息更新成功")


@router.put("/users/{user_id}/status", response_model=ApiResponse[UserResponse])
async def update_user_status(
    user_id: int,
    new_status: UserStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新用户状态（管理员）"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能修改自己的状态
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的状态"
        )
    
    # 对管理员的状态修改进行特殊限制
    if user.role == UserRole.ADMIN and new_status in [UserStatus.SUSPENDED, UserStatus.DELETED]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能暂停或删除管理员账户"
        )
    
    # 记录当前状态用于日志
    old_status = user.status
    
    user_update = UserUpdate(status=new_status)
    updated_user = update_user(db, user_id, user_update)
    
    status_text = {
        UserStatus.ACTIVE: "激活",
        UserStatus.INACTIVE: "未激活", 
        UserStatus.SUSPENDED: "暂停",
        UserStatus.DELETED: "删除"
    }.get(new_status, "更新")
    
    return ApiResponse.success_response(
        data=updated_user, 
        message=f"用户状态从 {old_status.value} 更新为 {status_text} 成功"
    )


@router.put("/users/{user_id}/role", response_model=ApiResponse[UserResponse])
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新用户角色（管理员）"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能修改自己的角色
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的角色"
        )
    
    user_update = UserUpdate(role=new_role)
    updated_user = update_user(db, user_id, user_update)
    
    role_text = {
        UserRole.ADMIN: "管理员",
        UserRole.MERCHANT: "商家",
        UserRole.USER: "普通用户",
        UserRole.CREW: "船员"
    }.get(new_role, "角色")
    
    return ApiResponse.success_response(data=updated_user, message=f"用户角色更新为{role_text}")


@router.put("/users/{user_id}/verify", response_model=ApiResponse[UserResponse])
async def verify_user(
    user_id: int,
    is_verified: bool = Query(..., description="是否验证"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """验证用户（管理员）"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_update = UserUpdate(is_verified=is_verified)
    updated_user = update_user(db, user_id, user_update)
    
    status_text = "验证通过" if is_verified else "取消验证"
    return ApiResponse.success_response(data=updated_user, message=f"用户{status_text}")


@router.get("/system/stats", response_model=ApiResponse[Dict[str, Any]])
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取系统统计信息（管理员）"""
    # 角色分布统计
    role_stats = {}
    for role in UserRole:
        pagination = PaginationParams(page=1, page_size=1)
        _, count = get_users(db, pagination, role=role)
        role_stats[role.value] = count
    
    # 状态分布统计
    status_stats = {}
    for user_status in UserStatus:
        pagination = PaginationParams(page=1, page_size=1)
        _, count = get_users(db, pagination, status=user_status)
        status_stats[user_status.value] = count
    
    # 验证状态统计
    pagination = PaginationParams(page=1, page_size=1)
    _, verified_count = get_users(db, pagination, is_verified=True)
    _, unverified_count = get_users(db, pagination, is_verified=False)
    
    stats_data = {
        "role_distribution": role_stats,
        "status_distribution": status_stats,
        "verification_stats": {
            "verified": verified_count,
            "unverified": unverified_count,
            "verification_rate": round(verified_count / (verified_count + unverified_count) * 100, 2) if (verified_count + unverified_count) > 0 else 0
        }
    }
    
    return ApiResponse.success_response(data=stats_data)


@router.delete("/users/{user_id}", response_model=ApiResponse[dict])
async def delete_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除用户（管理员）"""
    # 检查用户是否存在
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    # 不能删除其他管理员（除非是超级管理员的概念）
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能删除管理员账户"
        )
    
    # 执行删除操作
    success = delete_user(db, user_id)
    if success:
        return ApiResponse.success_response(
            data={"deleted_user_id": user_id},
            message="用户删除成功"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败"
        )


@router.post("/users/{user_id}/soft-delete", response_model=ApiResponse[UserResponse])
async def soft_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """软删除用户（将状态设置为已删除）（管理员）"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    # 不能删除其他管理员
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能删除管理员账户"
        )
    
    # 将用户状态设置为已删除
    user_update = UserUpdate(status=UserStatus.DELETED)
    updated_user = update_user(db, user_id, user_update)
    
    return ApiResponse.success_response(
        data=updated_user, 
        message="用户已被软删除"
    )

@router.post("/users/batch-operation", response_model=ApiResponse[dict])
async def batch_user_operation(
    user_ids: List[int] = Query(..., description="用户ID列表"),
    operation: str = Query(..., description="操作类型: activate, suspend, soft_delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """批量用户操作（管理员）"""
    
    if not user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户ID列表不能为空"
        )
    
    valid_operations = ["activate", "suspend", "soft_delete"]
    if operation not in valid_operations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的操作类型，支持的操作: {', '.join(valid_operations)}"
        )
    
    # 检查是否包含当前用户
    if current_user.id in user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能对自己执行批量操作"
        )
    
    # 检查是否包含管理员
    admin_users = db.query(User).filter(
        User.id.in_(user_ids),
        User.role == UserRole.ADMIN
    ).all()
    
    if admin_users and operation in ["suspend", "soft_delete"]:
        admin_usernames = [u.username for u in admin_users]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"不能对管理员执行此操作: {', '.join(admin_usernames)}"
        )
    
    # 执行批量操作
    operation_map = {
        "activate": UserStatus.ACTIVE,
        "suspend": UserStatus.SUSPENDED,
        "soft_delete": UserStatus.DELETED
    }
    
    new_status = operation_map[operation]
    affected_count = db.query(User).filter(User.id.in_(user_ids)).update(
        {User.status: new_status},
        synchronize_session=False
    )
    
    db.commit()
    
    operation_names = {
        "activate": "激活",
        "suspend": "暂停",
        "soft_delete": "软删除"
    }
    
    return ApiResponse.success_response(
        data={
            "operation": operation,
            "affected_count": affected_count,
            "user_ids": user_ids
        },
                 message=f"成功{operation_names[operation]}了 {affected_count} 个用户"
     )


@router.get("/users/status-summary", response_model=ApiResponse[Dict[str, Any]])
async def get_user_status_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取用户状态汇总（管理员）"""
    # 按状态统计用户数量
    status_summary = {}
    total_users = 0
    
    for status in UserStatus:
        pagination = PaginationParams(page=1, page_size=1)
        _, count = get_users(db, pagination, status=status)
        status_summary[status.value] = {
            "count": count,
            "percentage": 0  # 稍后计算
        }
        total_users += count
    
    # 计算百分比
    for status_data in status_summary.values():
        if total_users > 0:
            status_data["percentage"] = round(status_data["count"] / total_users * 100, 2)
    
    # 按角色和状态的交叉统计
    role_status_matrix = {}
    for role in UserRole:
        role_status_matrix[role.value] = {}
        for status in UserStatus:
            pagination = PaginationParams(page=1, page_size=1)
            _, count = get_users(db, pagination, role=role, status=status)
            role_status_matrix[role.value][status.value] = count
    
    # 实名认证统计
    pagination = PaginationParams(page=1, page_size=1)
    _, verified_count = get_users(db, pagination, is_verified=True)
    _, unverified_count = get_users(db, pagination, is_verified=False)
    
    summary_data = {
        "total_users": total_users,
        "status_distribution": status_summary,
        "role_status_matrix": role_status_matrix,
        "verification_summary": {
            "verified": verified_count,
            "unverified": unverified_count,
            "verification_rate": round(verified_count / total_users * 100, 2) if total_users > 0 else 0
        },
        "active_user_rate": round(
            status_summary.get("active", {}).get("count", 0) / total_users * 100, 2
        ) if total_users > 0 else 0
    }
    
    return ApiResponse.success_response(
        data=summary_data,
        message="用户状态汇总获取成功"
    )


@router.get("/users/recent-activities", response_model=ApiResponse[Dict[str, Any]])
async def get_recent_user_activities(
    days: int = Query(7, ge=1, le=30, description="查询最近天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取最近用户活动统计（管理员）"""
    from datetime import datetime, timedelta
    
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 查询最近注册的用户
    recent_registrations = db.query(User).filter(
        User.created_at >= start_date
    ).count()
    
    # 查询最近登录的用户
    recent_logins = db.query(User).filter(
        User.last_login_at >= start_date
    ).count()
    
    # 查询最近活跃用户（有登录记录且状态为激活）
    active_users = db.query(User).filter(
        User.status == UserStatus.ACTIVE,
        User.last_login_at >= start_date
    ).count()
    
    # 按角色统计最近注册用户
    role_registration_stats = {}
    for role in UserRole:
        count = db.query(User).filter(
            User.created_at >= start_date,
            User.role == role
        ).count()
        role_registration_stats[role.value] = count
    
    activity_data = {
        "date_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "recent_registrations": recent_registrations,
        "recent_logins": recent_logins,
        "active_users": active_users,
        "role_registration_breakdown": role_registration_stats,
        "activity_rate": round(
            recent_logins / recent_registrations * 100, 2
        ) if recent_registrations > 0 else 0
    }
    
    return ApiResponse.success_response(
        data=activity_data,
        message=f"最近 {days} 天用户活动统计获取成功"
    ) 
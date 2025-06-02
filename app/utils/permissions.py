from typing import List, Union
from functools import wraps
from fastapi import HTTPException, status, Depends

from app.models.user import User, UserRole
from .jwt_handler import get_current_active_user


def require_role(allowed_roles: Union[UserRole, List[UserRole]]):
    """角色权限装饰器"""
    if isinstance(allowed_roles, UserRole):
        allowed_roles = [allowed_roles]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 从kwargs中查找current_user参数
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要身份验证"
                )
            
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_permissions(permissions: List[str]):
    """权限验证装饰器（扩展用，目前基于角色）"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 从kwargs中查找current_user参数
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="需要身份验证"
                )
            
            # 基于角色的权限检查
            user_permissions = get_user_permissions(current_user.role)
            
            for permission in permissions:
                if permission not in user_permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"缺少权限: {permission}"
                    )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_user_permissions(role: UserRole) -> List[str]:
    """获取用户角色对应的权限列表"""
    permission_map = {
        UserRole.ADMIN: [
            "user:read", "user:write", "user:delete",
            "merchant:read", "merchant:write", "merchant:delete", "merchant:approve",
            "crew:read", "crew:write", "crew:delete", "crew:approve",
            "boat:read", "boat:write", "boat:delete",
            "service:read", "service:write", "service:delete",
            "product:read", "product:write", "product:delete",
            "order:read", "order:write", "order:delete", "order:manage",
            "payment:read", "payment:write", "payment:manage",
            "system:config", "system:monitor",
            "notification:send", "notification:manage"
        ],
        UserRole.MERCHANT: [
            "merchant:read", "merchant:write",
            "boat:read", "boat:write",
            "service:read", "service:write",
            "product:read", "product:write",
            "order:read", "order:write",
            "crew:read", "crew:manage",
            "schedule:read", "schedule:write",
            "review:read"
        ],
        UserRole.CREW: [
            "crew:read",
            "schedule:read",
            "boat:read",
            "service:read",
            "order:read"
        ],
        UserRole.TOURIST: [
            "service:read",
            "product:read",
            "order:read", "order:create",
            "review:read", "review:write",
            "user:read"
        ]
    }
    
    return permission_map.get(role, [])


def check_resource_owner(current_user: User, resource_user_id: int) -> bool:
    """检查是否为资源所有者"""
    return current_user.id == resource_user_id or current_user.role == UserRole.ADMIN


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """管理员权限依赖"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


def require_merchant(current_user: User = Depends(get_current_active_user)) -> User:
    """商家权限依赖"""
    if current_user.role not in [UserRole.MERCHANT, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要商家权限"
        )
    return current_user


def require_crew(current_user: User = Depends(get_current_active_user)) -> User:
    """船员权限依赖"""
    if current_user.role not in [UserRole.CREW, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要船员权限"
        )
    return current_user 
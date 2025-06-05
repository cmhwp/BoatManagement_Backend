from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from app.config.database import get_db
from app.utils.security import verify_token
from app.crud.user import get_user_by_id
from app.models.user import User
from app.models.enums import UserRole, UserStatus

# HTTP Bearer 认证方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户依赖项"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None or token_data.user_id is None:
        raise credentials_exception
    
    user = get_user_by_id(db, user_id=token_data.user_id)
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户依赖项"""
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="用户账号已被停用")
    return current_user


def require_roles(allowed_roles: List[UserRole]):
    """创建角色权限检查依赖项"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker


async def get_current_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """获取当前已实名认证用户依赖项"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要完成实名认证才能使用此功能"
        )
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """获取当前管理员用户依赖项"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


# 预定义的角色依赖项函数
require_admin = require_roles([UserRole.ADMIN])
require_merchant = require_roles([UserRole.ADMIN, UserRole.MERCHANT])
require_crew = require_roles([UserRole.ADMIN, UserRole.CREW])
require_user = require_roles([UserRole.ADMIN, UserRole.MERCHANT, UserRole.USER, UserRole.CREW]) 
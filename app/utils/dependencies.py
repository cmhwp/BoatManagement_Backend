from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils.jwt_handler import verify_token
from app.crud.user import crud_user

# HTTP Bearer 安全方案
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取当前登录用户（必需认证）"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证令牌"
        )
    
    # 验证并解析token
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌格式错误"
        )
    
    # 获取用户信息
    user = crud_user.get(db, id=int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if not crud_user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: Session = Depends(get_db)
):
    """获取当前登录用户（可选认证）"""
    if not credentials:
        return None
    
    try:
        # 验证并解析token
        payload = verify_token(credentials.credentials)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # 获取用户信息
        user = crud_user.get(db, id=int(user_id))
        if not user or not crud_user.is_active(user):
            return None
        
        return user
    except:
        return None


def require_role(*allowed_roles):
    """角色权限装饰器工厂"""
    def role_dependency(current_user = Depends(get_current_user)):
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_dependency


def require_admin(current_user = Depends(get_current_user)):
    """需要管理员权限"""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


def require_merchant(current_user = Depends(get_current_user)):
    """需要商家权限"""
    if current_user.role.value not in ["merchant", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要商家权限"
        )
    return current_user


def require_crew(current_user = Depends(get_current_user)):
    """需要船员权限"""
    if current_user.role.value not in ["crew", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要船员权限"
        )
    return current_user


def require_resource_owner(resource_user_id: int):
    """需要资源拥有者权限"""
    def owner_dependency(current_user = Depends(get_current_user)):
        if current_user.id != resource_user_id and current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能操作自己的资源"
            )
        return current_user
 
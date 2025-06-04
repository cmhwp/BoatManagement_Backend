from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.schemas.user import UserUpdate, UserResponse
from app.schemas.common import PaginatedResponse, PaginationParams, ApiResponse, MessageResponse
from app.crud.user import get_user_by_id, update_user
from app.utils.deps import get_current_active_user, require_roles
from app.models.user import User
from app.models.enums import UserRole

router = APIRouter(prefix="/users", tags=["users"])


@router.put("/me", response_model=ApiResponse[UserResponse], summary="更新当前用户信息")
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新当前登录用户的信息
    
    - **username**: 用户名
    - **email**: 邮箱地址
    - **phone**: 手机号
    - **real_name**: 真实姓名
    - **gender**: 性别
    - **address**: 地址
    - **avatar**: 头像URL
    """
    updated_user = update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到"
        )
    return ApiResponse.success_response(
        data=UserResponse.model_validate(updated_user),
        message="用户信息更新成功"
    )


@router.get("/{user_id}", response_model=ApiResponse[UserResponse], summary="获取用户详情")
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MERCHANT])),
    db: Session = Depends(get_db)
):
    """
    获取指定用户的详细信息
    
    权限要求：管理员或商家
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到"
        )
    return ApiResponse.success_response(
        data=UserResponse.model_validate(user),
        message="获取用户信息成功"
    )


@router.put("/{user_id}", response_model=ApiResponse[UserResponse], summary="更新用户信息")
async def update_user_info(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    更新指定用户的信息
    
    权限要求：管理员
    """
    updated_user = update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到"
        )
    return ApiResponse.success_response(
        data=UserResponse.model_validate(updated_user),
        message="用户信息更新成功"
    ) 
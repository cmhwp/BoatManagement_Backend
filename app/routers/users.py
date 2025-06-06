from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.config.database import get_db
from app.schemas.user import UserUpdate, UserResponse
from app.schemas.common import PaginatedResponse, PaginationParams, ApiResponse, MessageResponse
from app.crud.user import get_user_by_id, update_user
from app.utils.deps import get_current_active_user, get_current_verified_user, require_roles
from app.models.user import User
from app.models.enums import UserRole

router = APIRouter(prefix="/api/v1/users", tags=["users"])


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


@router.get("/me/verification-status", response_model=ApiResponse[dict], summary="获取实名认证状态")
async def get_verification_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的实名认证状态
    
    返回用户是否已实名认证及相关信息
    """
    from app.crud.identity_verification import identity_verification
    
    verification = identity_verification.get_by_user_id(db=db, user_id=current_user.id)
    
    if not verification:
        status_info = {
            "is_verified": False,
            "status": None,
            "message": "尚未提交实名认证申请"
        }
    else:
        status_info = {
            "is_verified": current_user.is_verified,
            "status": verification.status.value,
            "message": {
                "pending": "实名认证正在审核中",
                "approved": "实名认证已通过",
                "rejected": "实名认证被拒绝",
                "expired": "实名认证已过期"
            }.get(verification.status.value, "未知状态"),
            "verified_at": verification.verified_at,
            "expires_at": verification.expires_at,
            "reject_reason": verification.reject_reason if verification.status.value == "rejected" else None
        }
    
    return ApiResponse.success_response(
        data=status_info,
        message="获取实名认证状态成功"
    )


@router.get("/me/profile", response_model=ApiResponse[dict], summary="获取用户完整档案")
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的完整档案信息
    
    包括基本信息、实名认证状态、角色信息等
    """
    from app.crud.identity_verification import identity_verification
    
    # 获取实名认证信息
    verification = identity_verification.get_by_user_id(db=db, user_id=current_user.id)
    
    profile = {
        "basic_info": UserResponse.model_validate(current_user),
        "verification_status": {
            "is_verified": current_user.is_verified,
            "has_application": verification is not None,
            "status": verification.status.value if verification else None,
            "verified_at": verification.verified_at if verification else None,
            "expires_at": verification.expires_at if verification else None
        },
        "role_info": {
            "role": current_user.role.value,
            "role_name": {
                "admin": "管理员",
                "merchant": "商家",
                "user": "普通用户", 
                "crew": "船员"
            }.get(current_user.role.value, "未知角色")
        },
        "account_status": {
            "status": current_user.status.value,
            "is_active": current_user.status.value == "active",
            "last_login_at": current_user.last_login_at
        }
    }
    
    return ApiResponse.success_response(
        data=profile,
        message="获取用户档案成功"
    )
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.config.database import get_db
from app.utils.deps import get_current_active_user, require_admin, require_merchant
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.merchant import (
    MerchantCreate, MerchantUpdate, MerchantResponse, 
    MerchantListResponse, MerchantVerification
)
from app.schemas.common import PaginatedResponse, PaginationParams, ApiResponse, MessageResponse
from app.crud.merchant import (
    create_merchant, get_merchant_by_id, get_merchant_by_user_id,
    get_merchant_by_license_no, get_merchants, update_merchant,
    verify_merchant, activate_merchant, delete_merchant
)

router = APIRouter(prefix="/api/v1/merchants", tags=["merchants"])


@router.post("/", response_model=ApiResponse[MerchantResponse])
async def create_merchant_info(
    merchant: MerchantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建商家信息"""
    # 检查用户角色
    if current_user.role not in [UserRole.ADMIN, UserRole.MERCHANT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员或商家用户可以创建商家信息"
        )
    
    # 普通商家只能创建自己的信息
    if current_user.role == UserRole.MERCHANT and merchant.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="商家只能创建自己的信息"
        )
    
    # 检查用户是否已有商家信息
    existing_merchant = get_merchant_by_user_id(db, merchant.user_id)
    if existing_merchant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户已有商家信息"
        )
    
    # 检查营业执照号是否已存在
    existing_license = get_merchant_by_license_no(db, merchant.business_license_no)
    if existing_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="营业执照号已存在"
        )
    
    db_merchant = create_merchant(db, merchant)
    return ApiResponse.success_response(data=db_merchant, message="商家信息创建成功")


@router.get("/", response_model=PaginatedResponse[MerchantListResponse])
async def list_merchants(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    is_verified: Optional[bool] = Query(None, description="是否已认证"),
    is_active: Optional[bool] = Query(None, description="是否活跃"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取商家列表（管理员）"""
    pagination = PaginationParams(page=page, page_size=page_size)
    merchants, total = get_merchants(
        db, pagination, is_verified=is_verified, 
        is_active=is_active, search=search
    )
    
    return PaginatedResponse.create(
        items=merchants, total=total, page=page, page_size=page_size
    )


@router.get("/me", response_model=ApiResponse[MerchantResponse])
async def get_my_merchant_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的商家信息"""
    merchant = get_merchant_by_user_id(db, current_user.id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到商家信息"
        )
    
    return ApiResponse.success_response(data=merchant)


@router.get("/{merchant_id}", response_model=ApiResponse[MerchantResponse])
async def get_merchant_detail(
    merchant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取商家详情"""
    merchant = get_merchant_by_id(db, merchant_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商家不存在"
        )
    
    # 权限检查：管理员可查看所有，商家只能查看自己的
    if current_user.role != UserRole.ADMIN and merchant.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return ApiResponse.success_response(data=merchant)


@router.put("/me", response_model=ApiResponse[MerchantResponse])
async def update_my_merchant_info(
    merchant_update: MerchantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新当前用户的商家信息"""
    merchant = get_merchant_by_user_id(db, current_user.id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到商家信息"
        )
    
    # 如果更新营业执照号，检查是否已存在
    if merchant_update.business_license_no:
        existing_license = get_merchant_by_license_no(db, merchant_update.business_license_no)
        if existing_license and existing_license.id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="营业执照号已存在"
            )
    
    updated_merchant = update_merchant(db, merchant.id, merchant_update)
    return ApiResponse.success_response(data=updated_merchant, message="商家信息更新成功")


@router.put("/{merchant_id}", response_model=ApiResponse[MerchantResponse])
async def update_merchant_info(
    merchant_id: int,
    merchant_update: MerchantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新商家信息（管理员）"""
    merchant = get_merchant_by_id(db, merchant_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商家不存在"
        )
    
    # 如果更新营业执照号，检查是否已存在
    if merchant_update.business_license_no:
        existing_license = get_merchant_by_license_no(db, merchant_update.business_license_no)
        if existing_license and existing_license.id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="营业执照号已存在"
            )
    
    updated_merchant = update_merchant(db, merchant_id, merchant_update)
    return ApiResponse.success_response(data=updated_merchant, message="商家信息更新成功")


@router.post("/{merchant_id}/verify", response_model=ApiResponse[MerchantResponse])
async def verify_merchant_info(
    merchant_id: int,
    verification: MerchantVerification,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """认证商家（管理员）"""
    merchant = verify_merchant(db, merchant_id, verification.is_verified)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商家不存在"
        )
    
    status_text = "认证通过" if verification.is_verified else "认证未通过"
    return ApiResponse.success_response(data=merchant, message=f"商家{status_text}")


@router.post("/{merchant_id}/activate", response_model=ApiResponse[MerchantResponse])
async def activate_merchant_account(
    merchant_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """激活/停用商家（管理员）"""
    merchant = activate_merchant(db, merchant_id, is_active)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商家不存在"
        )
    
    status_text = "激活" if is_active else "停用"
    return ApiResponse.success_response(data=merchant, message=f"商家{status_text}成功")


@router.delete("/{merchant_id}", response_model=ApiResponse[MessageResponse])
async def delete_merchant_info(
    merchant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除商家（管理员）"""
    success = delete_merchant(db, merchant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商家不存在"
        )
    
    return ApiResponse.success_response(
        data=MessageResponse(message="商家删除成功"),
        message="商家删除成功"
    ) 
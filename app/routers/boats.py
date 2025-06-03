from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.config.database import get_db
from app.utils.deps import get_current_active_user, require_admin, require_merchant
from app.models.user import User
from app.models.enums import UserRole, BoatType, BoatStatus
from app.schemas.boat import (
    BoatCreate, BoatUpdate, BoatResponse, 
    BoatListResponse, BoatStatusUpdate
)
from app.schemas.common import PaginatedResponse, PaginationParams, ApiResponse, MessageResponse
from app.crud.boat import (
    create_boat, get_boat_by_id, get_boat_by_registration_no,
    get_boats, get_available_boats, get_merchant_boats,
    update_boat, update_boat_status, update_boat_location, delete_boat
)
from app.crud.merchant import get_merchant_by_user_id

router = APIRouter(prefix="/api/v1/boats", tags=["boats"])


@router.post("/", response_model=ApiResponse[BoatResponse])
async def create_boat_info(
    boat: BoatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建船艇信息"""
    # 检查用户角色
    if current_user.role not in [UserRole.ADMIN, UserRole.MERCHANT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员或商家可以创建船艇信息"
        )
    
    # 如果是商家，检查是否是自己的船艇
    if current_user.role == UserRole.MERCHANT:
        merchant = get_merchant_by_user_id(db, current_user.id)
        if not merchant or merchant.id != boat.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家只能为自己创建船艇信息"
            )
    
    # 检查注册编号是否已存在
    existing_boat = get_boat_by_registration_no(db, boat.registration_no)
    if existing_boat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="注册编号已存在"
        )
    
    db_boat = create_boat(db, boat)
    return ApiResponse.success_response(data=db_boat, message="船艇信息创建成功")


@router.get("/", response_model=PaginatedResponse[BoatListResponse])
async def list_boats(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    merchant_id: Optional[int] = Query(None, description="商家ID"),
    boat_type: Optional[BoatType] = Query(None, description="船艇类型"),
    status: Optional[BoatStatus] = Query(None, description="船艇状态"),
    is_available: Optional[bool] = Query(None, description="是否可用"),
    min_capacity: Optional[int] = Query(None, description="最小载客量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取船艇列表（管理员）"""
    pagination = PaginationParams(page=page, page_size=page_size)
    boats, total = get_boats(
        db, pagination, merchant_id=merchant_id, boat_type=boat_type,
        status=status, is_available=is_available, min_capacity=min_capacity,
        search=search
    )
    
    return PaginatedResponse.create(
        items=boats, total=total, page=page, page_size=page_size
    )


@router.get("/available", response_model=PaginatedResponse[BoatListResponse])
async def list_available_boats(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    boat_type: Optional[BoatType] = Query(None, description="船艇类型"),
    min_capacity: Optional[int] = Query(None, description="最小载客量"),
    location: Optional[str] = Query(None, description="位置"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取可用船艇列表"""
    # 所有已登录用户都可以查看可用船艇
    pagination = PaginationParams(page=page, page_size=page_size)
    boats, total = get_available_boats(
        db, pagination, boat_type=boat_type,
        min_capacity=min_capacity, location=location
    )
    
    return PaginatedResponse.create(
        items=boats, total=total, page=page, page_size=page_size
    )


@router.get("/my", response_model=PaginatedResponse[BoatListResponse])
async def list_my_boats(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[BoatStatus] = Query(None, description="船艇状态"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前商家的船艇列表"""
    # 检查用户是否是商家
    if current_user.role != UserRole.MERCHANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有商家可以查看自己的船艇列表"
        )
    
    merchant = get_merchant_by_user_id(db, current_user.id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到商家信息"
        )
    
    pagination = PaginationParams(page=page, page_size=page_size)
    boats, total = get_merchant_boats(db, merchant.id, pagination, status=status)
    
    return PaginatedResponse.create(
        items=boats, total=total, page=page, page_size=page_size
    )


@router.get("/{boat_id}", response_model=ApiResponse[BoatResponse])
async def get_boat_detail(
    boat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取船艇详情"""
    boat = get_boat_by_id(db, boat_id)
    if not boat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船艇不存在"
        )
    
    # 权限检查：管理员可查看所有，商家只能查看自己的
    if current_user.role == UserRole.MERCHANT:
        merchant = get_merchant_by_user_id(db, current_user.id)
        if not merchant or boat.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    elif current_user.role not in [UserRole.ADMIN, UserRole.USER, UserRole.CREW]:
        # 其他角色需要权限检查
        pass
    
    return ApiResponse.success_response(data=boat)


@router.put("/{boat_id}", response_model=ApiResponse[BoatResponse])
async def update_boat_info(
    boat_id: int,
    boat_update: BoatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新船艇信息"""
    boat = get_boat_by_id(db, boat_id)
    if not boat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船艇不存在"
        )
    
    # 权限检查：管理员可更新所有，商家只能更新自己的
    if current_user.role == UserRole.MERCHANT:
        merchant = get_merchant_by_user_id(db, current_user.id)
        if not merchant or boat.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家只能更新自己的船艇信息"
            )
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    updated_boat = update_boat(db, boat_id, boat_update)
    return ApiResponse.success_response(data=updated_boat, message="船艇信息更新成功")


@router.put("/{boat_id}/status", response_model=ApiResponse[BoatResponse])
async def update_boat_status_info(
    boat_id: int,
    status_update: BoatStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新船艇状态"""
    boat = get_boat_by_id(db, boat_id)
    if not boat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船艇不存在"
        )
    
    # 权限检查：管理员、商家或船员可以更新状态
    if current_user.role == UserRole.MERCHANT:
        merchant = get_merchant_by_user_id(db, current_user.id)
        if not merchant or boat.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家只能更新自己的船艇状态"
            )
    elif current_user.role not in [UserRole.ADMIN, UserRole.CREW]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    updated_boat = update_boat_status(
        db, boat_id, status_update.status, 
        status_update.is_available, status_update.current_location
    )
    return ApiResponse.success_response(data=updated_boat, message="船艇状态更新成功")


@router.put("/{boat_id}/location", response_model=ApiResponse[BoatResponse])
async def update_boat_location_info(
    boat_id: int,
    location: str = Query(..., description="位置信息"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新船艇位置"""
    boat = get_boat_by_id(db, boat_id)
    if not boat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船艇不存在"
        )
    
    # 权限检查：管理员、商家或船员可以更新位置
    if current_user.role == UserRole.MERCHANT:
        merchant = get_merchant_by_user_id(db, current_user.id)
        if not merchant or boat.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家只能更新自己的船艇位置"
            )
    elif current_user.role not in [UserRole.ADMIN, UserRole.CREW]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    updated_boat = update_boat_location(db, boat_id, location)
    return ApiResponse.success_response(data=updated_boat, message="船艇位置更新成功")


@router.delete("/{boat_id}", response_model=ApiResponse[MessageResponse])
async def delete_boat_info(
    boat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除船艇"""
    boat = get_boat_by_id(db, boat_id)
    if not boat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船艇不存在"
        )
    
    # 权限检查：管理员可删除所有，商家只能删除自己的
    if current_user.role == UserRole.MERCHANT:
        merchant = get_merchant_by_user_id(db, current_user.id)
        if not merchant or boat.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家只能删除自己的船艇"
            )
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    success = delete_boat(db, boat_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船艇不存在"
        )
    
    return ApiResponse.success_response(
        data=MessageResponse(message="船艇删除成功"),
        message="船艇删除成功"
    ) 
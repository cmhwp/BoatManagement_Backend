from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.models.enums import ServiceStatus, ServiceType, UserRole
from app.schemas.service import (
    ServiceCreate, ServiceUpdate, ServiceResponse, ServiceListResponse
)
from app.schemas.common import ApiResponse, PaginatedResponse
from app.utils.deps import get_current_user, require_roles
from app.crud import service as service_crud
from app.crud import merchant as merchant_crud

router = APIRouter(prefix="/api/v1/services", tags=["service"])


# =============================================================================
# 公共服务接口
# =============================================================================

@router.get("/", response_model=ApiResponse[List[ServiceListResponse]], summary="获取服务列表")
async def get_services(
    service_type: Optional[ServiceType] = Query(None, description="服务类型筛选"),
    merchant_id: Optional[int] = Query(None, description="商家ID筛选"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    location: Optional[str] = Query(None, description="地点筛选"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """获取服务列表"""
    services = service_crud.get_services(
        db=db,
        service_type=service_type,
        merchant_id=merchant_id,
        min_price=min_price,
        max_price=max_price,
        location=location,
        skip=skip,
        limit=limit,
        search=search
    )
    
    return ApiResponse(
        success=True,
        data=services
    )


@router.get("/available", response_model=ApiResponse[List[ServiceListResponse]], summary="获取可用服务")
async def get_available_services(
    service_type: Optional[ServiceType] = Query(None, description="服务类型筛选"),
    location: Optional[str] = Query(None, description="地点筛选"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取可用服务列表"""
    services = service_crud.get_available_services(
        db=db,
        service_type=service_type,
        location=location,
        skip=skip,
        limit=limit
    )
    
    return ApiResponse(
        success=True,
        data=services
    )


@router.get("/{service_id}", response_model=ApiResponse[ServiceResponse], summary="获取服务详情")
async def get_service_detail(
    service_id: int,
    db: Session = Depends(get_db)
):
    """获取服务详细信息"""
    service = service_crud.get_service_detail(db, service_id)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    return ApiResponse(
        success=True,
        data=service
    )


# =============================================================================
# 商家服务管理接口
# =============================================================================

@router.post("/", response_model=ApiResponse[ServiceResponse], summary="创建服务")
async def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MERCHANT, UserRole.ADMIN]))
):
    """创建新服务"""
    # 获取商家信息
    merchant = merchant_crud.get_merchant_by_user_id(db, current_user.id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商家信息不存在，请先完善商家资料"
        )
    
    try:
        service = service_crud.create_service(
            db=db,
            service_data=service_data,
            merchant_id=merchant.id
        )
        
        return ApiResponse(
            success=True,
            message="服务创建成功",
            data=service
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建服务失败: {str(e)}"
        )


@router.get("/my", response_model=ApiResponse[List[ServiceListResponse]], summary="获取我的服务")
async def get_my_services(
    status: Optional[ServiceStatus] = Query(None, description="服务状态筛选"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MERCHANT, UserRole.ADMIN]))
):
    """获取当前商家的服务列表"""
    # 获取商家信息
    merchant = merchant_crud.get_merchant_by_user_id(db, current_user.id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商家信息不存在"
        )
    
    services = service_crud.get_services_by_merchant(
        db=db,
        merchant_id=merchant.id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return ApiResponse(
        success=True,
        data=services
    )


@router.put("/{service_id}", response_model=ApiResponse[ServiceResponse], summary="更新服务信息")
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MERCHANT, UserRole.ADMIN]))
):
    """更新服务信息"""
    # 检查服务是否存在
    service = service_crud.get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    # 检查权限（非管理员只能修改自己的服务）
    if current_user.role != UserRole.ADMIN:
        merchant = merchant_crud.get_merchant_by_user_id(db, current_user.id)
        if not merchant or service.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此服务"
            )
    
    updated_service = service_crud.update_service(db, service_id, service_data)
    
    if not updated_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="服务更新失败"
        )
    
    return ApiResponse(
        success=True,
        message="服务信息已更新",
        data=updated_service
    )


@router.delete("/{service_id}", response_model=ApiResponse[dict], summary="删除服务")
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MERCHANT, UserRole.ADMIN]))
):
    """删除服务"""
    # 检查服务是否存在
    service = service_crud.get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    # 检查权限（非管理员只能删除自己的服务）
    if current_user.role != UserRole.ADMIN:
        merchant = merchant_crud.get_merchant_by_user_id(db, current_user.id)
        if not merchant or service.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此服务"
            )
    
    # 检查是否有关联的订单
    if service_crud.has_active_orders(db, service_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该服务存在进行中的订单，无法删除"
        )
    
    success = service_crud.delete_service(db, service_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="服务删除失败"
        )
    
    return ApiResponse(
        success=True,
        message="服务已删除",
        data={}
    ) 
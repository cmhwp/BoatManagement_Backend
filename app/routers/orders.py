from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.models.merchant import Merchant
from app.models.crew_info import CrewInfo
from app.models.enums import OrderStatus, UserRole
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse, 
    OrderAssignCrew, OrderStatusUpdate, OrderStats
)
from app.schemas.common import ApiResponse, PaginatedResponse
from app.utils.deps import get_current_user, require_roles
from app.crud import order as order_crud
from app.crud import merchant as merchant_crud
from app.crud import crew as crew_crud

router = APIRouter(prefix="/api/v1/orders", tags=["order"])


# =============================================================================
# 用户订单接口
# =============================================================================

@router.post("/", response_model=ApiResponse[OrderResponse], summary="创建订单")
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新的预约订单
    
    - **order_type**: 订单类型（service/product）
    - **service_id**: 服务ID（服务订单必需）
    - **scheduled_at**: 预约服务时间
    - **participants**: 参与人数
    - **contact_name**: 联系人姓名
    - **contact_phone**: 联系电话
    """
    try:
        # 获取服务的商家ID
        merchant_id = None
        if order_data.service_id:
            from app.crud import service as service_crud
            service = service_crud.get_service_by_id(db, order_data.service_id)
            if not service:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="服务不存在"
                )
            merchant_id = service.merchant_id
        
        if not merchant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法确定服务提供商"
            )
        
        # 创建订单
        order = order_crud.create_order(
            db=db,
            order_data=order_data,
            user_id=current_user.id,
            merchant_id=merchant_id
        )
        
        return ApiResponse(
            success=True,
            message="订单创建成功",
            data=order
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建订单失败: {str(e)}"
        )


@router.get("/my", response_model=ApiResponse[List[OrderListResponse]], summary="获取我的订单")
async def get_my_orders(
    status: Optional[OrderStatus] = Query(None, description="订单状态筛选"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的所有订单"""
    orders = order_crud.get_orders_by_user(
        db=db,
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return ApiResponse(
        success=True,
        data=orders
    )


@router.get("/my/{order_id}", response_model=ApiResponse[OrderResponse], summary="获取订单详情")
async def get_my_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取订单详细信息"""
    order = order_crud.get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 检查权限：只能查看自己的订单
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此订单"
        )
    
    return ApiResponse(
        success=True,
        data=order
    )


@router.post("/my/{order_id}/cancel", response_model=ApiResponse[OrderResponse], summary="取消订单")
async def cancel_my_order(
    order_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消订单"""
    order = order_crud.get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 检查权限：只能取消自己的订单
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此订单"
        )
    
    # 取消订单
    cancelled_order = order_crud.cancel_order(db, order_id, reason)
    
    if not cancelled_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单当前状态不允许取消"
        )
    
    return ApiResponse(
        success=True,
        message="订单已取消",
        data=cancelled_order
    )


# =============================================================================
# 商家订单管理接口
# =============================================================================

@router.get("/merchant", response_model=ApiResponse[List[OrderListResponse]], summary="获取商家订单")
async def get_merchant_orders(
    status: Optional[OrderStatus] = Query(None, description="订单状态筛选"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MERCHANT, UserRole.ADMIN]))
):
    """获取商家的所有订单"""
    # 获取商家信息
    merchant = merchant_crud.get_merchant_by_user_id(db, current_user.id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商家信息不存在"
        )
    
    orders = order_crud.get_orders_by_merchant(
        db=db,
        merchant_id=merchant.id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return ApiResponse(
        success=True,
        data=orders
    )


@router.post("/merchant/{order_id}/assign-crew", response_model=ApiResponse[OrderResponse], summary="派单给船员")
async def assign_crew_to_order(
    order_id: int,
    assign_data: OrderAssignCrew,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MERCHANT, UserRole.ADMIN]))
):
    """
    为订单指派船员（核心派单功能）
    
    - **crew_id**: 指派的船员ID
    - **boat_id**: 指定的船艇ID（可选）
    - **notes**: 派单备注
    """
    # 获取商家信息
    merchant = merchant_crud.get_merchant_by_user_id(db, current_user.id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商家信息不存在"
        )
    
    # 检查订单权限
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.merchant_id != merchant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此订单"
        )
    
    # 检查订单状态
    if order.status not in [OrderStatus.PAID, OrderStatus.PENDING_ASSIGNMENT]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单当前状态不允许派单"
        )
    
    # 执行派单
    assigned_order = order_crud.assign_crew_to_order(db, order_id, assign_data)
    
    if not assigned_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="派单失败，请检查船员可用性或时间冲突"
        )
    
    return ApiResponse(
        success=True,
        message="派单成功",
        data=assigned_order
    )


@router.put("/merchant/{order_id}/status", response_model=ApiResponse[OrderResponse], summary="更新订单状态")
async def update_merchant_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MERCHANT, UserRole.ADMIN]))
):
    """商家更新订单状态"""
    # 获取商家信息
    merchant = merchant_crud.get_merchant_by_user_id(db, current_user.id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商家信息不存在"
        )
    
    # 检查订单权限
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.merchant_id != merchant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此订单"
        )
    
    # 更新状态
    updated_order = order_crud.update_order_status(db, order_id, status_data)
    
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="状态更新失败"
        )
    
    return ApiResponse(
        success=True,
        message="订单状态已更新",
        data=updated_order
    )


@router.get("/merchant/{order_id}/available-crews", response_model=ApiResponse[List], summary="获取可派单船员")
async def get_available_crews_for_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MERCHANT, UserRole.ADMIN]))
):
    """获取订单可用的船员列表"""
    # 获取商家信息
    merchant = merchant_crud.get_merchant_by_user_id(db, current_user.id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商家信息不存在"
        )
    
    # 检查订单权限
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.merchant_id != merchant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此订单信息"
        )
    
    # 获取可用船员
    available_crews = order_crud.get_available_crews_for_order(db, order_id)
    
    return ApiResponse(
        success=True,
        data=available_crews
    )


@router.get("/merchant/stats", response_model=ApiResponse[OrderStats], summary="商家订单统计")
async def get_merchant_order_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.MERCHANT, UserRole.ADMIN]))
):
    """获取商家订单统计数据"""
    # 获取商家信息
    merchant = merchant_crud.get_merchant_by_user_id(db, current_user.id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商家信息不存在"
        )
    
    stats = order_crud.get_merchant_order_stats(db, merchant.id)
    
    return ApiResponse(
        success=True,
        data=stats
    )


# =============================================================================
# 船员订单接口
# =============================================================================

@router.get("/crew/my", response_model=ApiResponse[List[OrderListResponse]], summary="获取我的船员订单")
async def get_my_crew_orders(
    status: Optional[OrderStatus] = Query(None, description="订单状态筛选"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.CREW, UserRole.ADMIN]))
):
    """获取分配给当前船员的订单"""
    # 获取船员信息
    crew = crew_crud.get_crew_by_user_id(db, current_user.id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船员信息不存在"
        )
    
    orders = order_crud.get_orders_by_crew(
        db=db,
        crew_id=crew.id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return ApiResponse(
        success=True,
        data=orders
    )


@router.put("/crew/{order_id}/status", response_model=ApiResponse[OrderResponse], summary="船员更新订单状态")
async def update_crew_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.CREW, UserRole.ADMIN]))
):
    """船员更新订单状态（如确认接单、开始服务等）"""
    # 获取船员信息
    crew = crew_crud.get_crew_by_user_id(db, current_user.id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="船员信息不存在"
        )
    
    # 检查订单权限
    order = order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.crew_id != crew.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此订单未分配给您"
        )
    
    # 船员只能更新特定状态
    allowed_statuses = [OrderStatus.IN_PROGRESS, OrderStatus.COMPLETED]
    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="船员只能更新订单为进行中或已完成状态"
        )
    
    # 更新状态
    updated_order = order_crud.update_order_status(db, order_id, status_data)
    
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="状态更新失败"
        )
    
    return ApiResponse(
        success=True,
        message="订单状态已更新",
        data=updated_order
    )
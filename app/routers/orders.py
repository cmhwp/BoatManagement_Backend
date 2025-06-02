from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderStatusUpdate,
    RefundRequest, OrderSummary
)
from app.services.order_service import OrderService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.dependencies import get_current_user, require_merchant
from app.models.order import OrderStatus, OrderType

router = APIRouter()


@router.post("", summary="创建订单")
async def create_order(
    order_create: OrderCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新订单"""
    try:
        result = OrderService.create_order(db, current_user.id, order_create)
        return success_response(
            message="订单创建成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/my-orders", summary="获取我的订单")
async def get_my_orders(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_type: Optional[OrderType] = Query(None, description="订单类型筛选"),
    status: Optional[OrderStatus] = Query(None, description="订单状态筛选"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的订单列表"""
    try:
        skip = (page - 1) * size
        result = OrderService.get_user_orders(
            db=db,
            user_id=current_user.id,
            order_type=order_type,
            status=status,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["orders"],
            total=result["total"],
            page=page,
            size=size,
            message="获取订单列表成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/merchant-orders", summary="获取商家订单")
async def get_merchant_orders(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_type: Optional[OrderType] = Query(None, description="订单类型筛选"),
    status: Optional[OrderStatus] = Query(None, description="订单状态筛选"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取商家的订单列表"""
    try:
        skip = (page - 1) * size
        result = OrderService.get_merchant_orders(
            db=db,
            user_id=current_user.id,
            order_type=order_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["orders"],
            total=result["total"],
            page=page,
            size=size,
            message="获取商家订单列表成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/summary", summary="获取订单统计")
async def get_order_summary(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户订单统计"""
    try:
        result = OrderService.get_order_summary(db, current_user.id)
        return success_response(
            message="获取订单统计成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/merchant-summary", summary="获取商家订单统计")
async def get_merchant_order_summary(
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取商家订单统计"""
    try:
        result = OrderService.get_merchant_order_summary(db, current_user.id)
        return success_response(
            message="获取商家订单统计成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/{order_id}", summary="获取订单详情")
async def get_order_detail(
    order_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取订单详细信息"""
    try:
        result = OrderService.get_order_detail(db, current_user.id, order_id)
        return success_response(
            message="获取订单详情成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.put("/{order_id}", summary="更新订单信息")
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新订单信息（仅限待支付状态）"""
    try:
        result = OrderService.update_order(db, current_user.id, order_id, order_update)
        return success_response(
            message="订单信息更新成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.patch("/{order_id}/cancel", summary="取消订单")
async def cancel_order(
    order_id: int,
    reason: Optional[str] = Query(None, description="取消原因"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消订单"""
    try:
        result = OrderService.cancel_order(db, current_user.id, order_id, reason)
        return success_response(
            message="订单取消成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.patch("/{order_id}/confirm", summary="确认订单")
async def confirm_order(
    order_id: int,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """确认订单（商家操作）"""
    try:
        result = OrderService.confirm_order(db, current_user.id, order_id)
        return success_response(
            message="订单确认成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.patch("/{order_id}/complete", summary="完成订单")
async def complete_order(
    order_id: int,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """完成订单（商家操作）"""
    try:
        result = OrderService.complete_order(db, current_user.id, order_id)
        return success_response(
            message="订单完成成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/{order_id}/refund", summary="申请退款")
async def request_refund(
    order_id: int,
    refund_request: RefundRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """申请订单退款"""
    try:
        result = OrderService.request_refund(db, current_user.id, order_id, refund_request)
        return success_response(
            message="退款申请提交成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code) 
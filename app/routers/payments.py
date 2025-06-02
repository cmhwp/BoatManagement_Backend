from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.schemas.payment import (
    PaymentCreate, PaymentUpdate, PaymentResponse, PaymentSearchFilter,
    RefundCreate, RefundUpdate, RefundResponse, PaymentCallback,
    PaymentStatistics, PaymentLinkResponse
)
from app.services.payment_service import PaymentService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.dependencies import get_current_user, require_admin

router = APIRouter()


@router.post("", summary="创建支付")
async def create_payment(
    payment_create: PaymentCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建支付记录并获取支付链接"""
    try:
        result = PaymentService.create_payment(db, current_user.id, payment_create)
        return success_response(
            message="支付创建成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/my-payments", summary="获取我的支付记录")
async def get_my_payments(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的支付记录列表"""
    try:
        skip = (page - 1) * size
        result = PaymentService.get_user_payments(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["payments"],
            total=result["total"],
            page=page,
            size=size,
            message="获取支付记录成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/search", summary="搜索支付记录")
async def search_payments(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_id: Optional[int] = Query(None, description="订单ID"),
    payment_method: Optional[str] = Query(None, description="支付方式"),
    status: Optional[str] = Query(None, description="支付状态"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    min_amount: Optional[float] = Query(None, description="最小金额"),
    max_amount: Optional[float] = Query(None, description="最大金额"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索支付记录"""
    try:
        skip = (page - 1) * size
        
        filter_params = PaymentSearchFilter(
            order_id=order_id,
            payment_method=payment_method,
            status=status,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            keyword=keyword
        )
        
        result = PaymentService.search_payments(
            db=db,
            user_id=current_user.id,
            filter_params=filter_params,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["payments"],
            total=result["total"],
            page=page,
            size=size,
            message="搜索支付记录成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/statistics", summary="获取支付统计")
async def get_payment_statistics(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取支付统计信息"""
    try:
        result = PaymentService.get_payment_statistics(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        return success_response(
            message="获取支付统计成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/{payment_id}", summary="获取支付详情")
async def get_payment_detail(
    payment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取支付详细信息"""
    try:
        result = PaymentService.get_payment_detail(db, current_user.id, payment_id)
        return success_response(
            message="获取支付详情成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.patch("/{payment_id}/cancel", summary="取消支付")
async def cancel_payment(
    payment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消支付"""
    try:
        result = PaymentService.cancel_payment(db, current_user.id, payment_id)
        return success_response(
            message="支付取消成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/callback", summary="支付回调")
async def payment_callback(
    callback_data: PaymentCallback,
    db: Session = Depends(get_db)
):
    """处理支付回调通知"""
    try:
        result = PaymentService.handle_payment_callback(db, callback_data)
        return success_response(
            message="回调处理成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/simulate-success/{payment_no}", summary="模拟支付成功")
async def simulate_payment_success(
    payment_no: str,
    db: Session = Depends(get_db)
):
    """模拟支付成功（仅用于测试）"""
    try:
        result = PaymentService.simulate_payment_success(db, payment_no)
        return success_response(
            message="模拟支付成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


# 退款相关接口
@router.post("/refunds", summary="申请退款")
async def create_refund(
    refund_create: RefundCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建退款申请"""
    try:
        result = PaymentService.create_refund(db, current_user.id, refund_create)
        return success_response(
            message="退款申请提交成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.patch("/refunds/{refund_id}", summary="处理退款申请")
async def process_refund(
    refund_id: int,
    refund_update: RefundUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """处理退款申请（管理员操作）"""
    try:
        result = PaymentService.process_refund(db, current_user.id, refund_id, refund_update)
        return success_response(
            message="退款处理成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code) 
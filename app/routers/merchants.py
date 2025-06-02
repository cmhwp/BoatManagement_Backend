from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.merchant import MerchantCreate, MerchantUpdate, MerchantResponse, MerchantVerification
from app.services.merchant_service import MerchantService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.dependencies import get_current_user, require_admin, require_merchant
from app.models.merchant import MerchantStatus, VerificationLevel

router = APIRouter()


@router.post("/register", summary="商家入驻申请")
async def register_merchant(
    merchant_create: MerchantCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商家入驻申请"""
    try:
        result = MerchantService.register_merchant(db, current_user.id, merchant_create)
        return success_response(
            message="商家入驻申请已提交",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/profile", summary="获取商家资料")
async def get_merchant_profile(
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取当前用户的商家资料"""
    try:
        result = MerchantService.get_merchant_profile(db, current_user.id)
        return success_response(
            message="获取商家资料成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.put("/profile", summary="更新商家资料")
async def update_merchant_profile(
    merchant_update: MerchantUpdate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """更新商家资料"""
    try:
        result = MerchantService.update_merchant_profile(db, current_user.id, merchant_update)
        return success_response(
            message="商家资料更新成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/{merchant_id}", summary="获取指定商家信息")
async def get_merchant(
    merchant_id: int,
    db: Session = Depends(get_db)
):
    """获取指定商家的公开信息"""
    try:
        result = MerchantService.get_merchant_by_id(db, merchant_id)
        return success_response(
            message="获取商家信息成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("", summary="获取商家列表")
async def get_merchants_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[MerchantStatus] = Query(None, description="商家状态筛选"),
    verification_level: Optional[VerificationLevel] = Query(None, description="认证级别筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """获取商家列表"""
    try:
        skip = (page - 1) * size
        result = MerchantService.get_merchants_list(
            db=db,
            skip=skip,
            limit=size,
            status=status,
            verification_level=verification_level,
            keyword=keyword
        )
        
        return paginated_response(
            data=result["merchants"],
            total=result["total"],
            page=page,
            size=size,
            message="获取商家列表成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/nearby", summary="获取附近商家")
async def get_nearby_merchants(
    latitude: float = Query(..., description="纬度"),
    longitude: float = Query(..., description="经度"),
    radius: float = Query(10.0, ge=1, le=50, description="搜索半径（公里）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取附近商家"""
    try:
        skip = (page - 1) * size
        result = MerchantService.get_nearby_merchants(
            db=db,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            skip=skip,
            limit=size
        )
        
        return success_response(
            message="获取附近商家成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


# 管理员功能
@router.post("/{merchant_id}/verify", summary="商家认证")
async def verify_merchant(
    merchant_id: int,
    verification: MerchantVerification,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """商家认证（管理员功能）"""
    try:
        result = MerchantService.verify_merchant(
            db, merchant_id, verification, current_user.id
        )
        return success_response(
            message="商家认证完成",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/{merchant_id}/suspend", summary="暂停商家")
async def suspend_merchant(
    merchant_id: int,
    reason: str = Query(..., description="暂停原因"),
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """暂停商家（管理员功能）"""
    try:
        result = MerchantService.suspend_merchant(
            db, merchant_id, current_user.id, reason
        )
        return success_response(
            message="商家已暂停",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code) 
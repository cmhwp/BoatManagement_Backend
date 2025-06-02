from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.database import get_db
from app.schemas.boat import (
    BoatCreate, BoatUpdate, BoatResponse, BoatStatusUpdate, 
    BoatMaintenanceUpdate
)
from app.services.boat_service import BoatService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.dependencies import get_current_user, get_current_user_optional, require_merchant
from app.models.boat import BoatStatus, BoatType

router = APIRouter()


@router.post("", summary="创建船艇")
async def create_boat(
    boat_create: BoatCreate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """创建新船艇（商家功能）"""
    try:
        result = BoatService.create_boat(db, current_user.id, boat_create)
        return success_response(
            message="船艇创建成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/my-boats", summary="获取我的船艇列表")
async def get_my_boats(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[BoatStatus] = Query(None, description="船艇状态筛选"),
    boat_type: Optional[BoatType] = Query(None, description="船艇类型筛选"),
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取商家的船艇列表"""
    try:
        skip = (page - 1) * size
        result = BoatService.get_merchant_boats(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=size,
            status=status,
            boat_type=boat_type
        )
        
        return paginated_response(
            data=result["boats"],
            total=result["total"],
            page=page,
            size=size,
            message="获取船艇列表成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/available", summary="获取可用船艇列表")
async def get_available_boats(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    boat_type: Optional[BoatType] = Query(None, description="船艇类型"),
    min_capacity: Optional[int] = Query(None, description="最小载客量"),
    max_hourly_rate: Optional[float] = Query(None, description="最大时租金"),
    location: Optional[str] = Query(None, description="位置搜索"),
    db: Session = Depends(get_db)
):
    """获取可用船艇列表（公开接口）"""
    try:
        skip = (page - 1) * size
        result = BoatService.get_available_boats(
            db=db,
            boat_type=boat_type,
            min_capacity=min_capacity,
            max_hourly_rate=max_hourly_rate,
            location=location,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["boats"],
            total=result["total"],
            page=page,
            size=size,
            message="获取可用船艇列表成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/maintenance-needed", summary="获取需要维护的船艇")
async def get_boats_need_maintenance(
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取需要维护的船艇列表（商家功能）"""
    try:
        result = BoatService.get_boats_need_maintenance(db, current_user.id)
        return success_response(
            message="获取维护提醒成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/{boat_id}", summary="获取船艇详情")
async def get_boat_detail(
    boat_id: int,
    current_user = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """获取船艇详细信息"""
    try:
        user_id = current_user.id if current_user else None
        result = BoatService.get_boat_detail(db, boat_id, user_id)
        return success_response(
            message="获取船艇详情成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.put("/{boat_id}", summary="更新船艇信息")
async def update_boat(
    boat_id: int,
    boat_update: BoatUpdate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """更新船艇信息（船艇所有者）"""
    try:
        result = BoatService.update_boat(db, current_user.id, boat_id, boat_update)
        return success_response(
            message="船艇信息更新成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.delete("/{boat_id}", summary="删除船艇")
async def delete_boat(
    boat_id: int,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """删除船艇（船艇所有者）"""
    try:
        result = BoatService.delete_boat(db, current_user.id, boat_id)
        return success_response(
            message="船艇删除成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.patch("/{boat_id}/status", summary="更新船艇状态")
async def update_boat_status(
    boat_id: int,
    status_update: BoatStatusUpdate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """更新船艇状态（船艇所有者）"""
    try:
        result = BoatService.update_boat_status(db, current_user.id, boat_id, status_update)
        return success_response(
            message="船艇状态更新成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.patch("/{boat_id}/maintenance", summary="更新船艇维护信息")
async def update_boat_maintenance(
    boat_id: int,
    maintenance_update: BoatMaintenanceUpdate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """更新船艇维护信息（船艇所有者）"""
    try:
        result = BoatService.update_boat_maintenance(db, current_user.id, boat_id, maintenance_update)
        return success_response(
            message="船艇维护信息更新成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/{boat_id}/upload-images", summary="上传船艇图片")
async def upload_boat_images(
    boat_id: int,
    files: List[UploadFile] = File(...),
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """上传船艇图片（船艇所有者）"""
    try:
        result = await BoatService.upload_boat_images(db, current_user.id, boat_id, files)
        return success_response(
            message="船艇图片上传成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code) 
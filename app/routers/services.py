from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.database import get_db
from app.schemas.service import (
    ServiceCreate, ServiceUpdate, ServiceResponse, ServiceStatusUpdate, 
    ServiceScheduleUpdate, ServiceSearchFilter
)
from app.services.service_service import ServiceService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.dependencies import get_current_user, get_current_user_optional, require_merchant
from app.models.service import ServiceStatus, ServiceType

router = APIRouter()


@router.post("", summary="创建服务")
async def create_service(
    service_create: ServiceCreate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """创建新服务（商家功能）"""
    try:
        result = ServiceService.create_service(db, current_user.id, service_create)
        return success_response(
            message="服务创建成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/my-services", summary="获取我的服务列表")
async def get_my_services(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[ServiceStatus] = Query(None, description="服务状态筛选"),
    service_type: Optional[ServiceType] = Query(None, description="服务类型筛选"),
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取商家的服务列表"""
    try:
        skip = (page - 1) * size
        result = ServiceService.get_merchant_services(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=size,
            status=status,
            service_type=service_type
        )
        
        return paginated_response(
            data=result["services"],
            total=result["total"],
            page=page,
            size=size,
            message="获取服务列表成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/search", summary="搜索服务")
async def search_services(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    service_type: Optional[ServiceType] = Query(None, description="服务类型"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    min_duration: Optional[int] = Query(None, description="最短时长"),
    max_duration: Optional[int] = Query(None, description="最长时长"),
    max_participants: Optional[int] = Query(None, description="最大参与人数"),
    is_green_service: Optional[bool] = Query(None, description="是否绿色服务"),
    region_id: Optional[int] = Query(None, description="地区ID"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """搜索可预订服务"""
    try:
        skip = (page - 1) * size
        
        filter_params = ServiceSearchFilter(
            service_type=service_type,
            min_price=min_price,
            max_price=max_price,
            min_duration=min_duration,
            max_duration=max_duration,
            max_participants=max_participants,
            is_green_service=is_green_service,
            region_id=region_id,
            keyword=keyword
        )
        
        result = ServiceService.get_available_services(
            db=db,
            filter_params=filter_params,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["services"],
            total=result["total"],
            page=page,
            size=size,
            message="搜索服务成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/featured", summary="获取推荐服务")
async def get_featured_services(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取推荐服务列表"""
    try:
        skip = (page - 1) * size
        result = ServiceService.get_featured_services(db, skip=skip, limit=size)
        
        return success_response(
            message="获取推荐服务成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/green", summary="获取绿色服务")
async def get_green_services(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取绿色服务列表"""
    try:
        skip = (page - 1) * size
        result = ServiceService.get_green_services(db, skip=skip, limit=size)
        
        return success_response(
            message="获取绿色服务成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/popular", summary="获取热门服务")
async def get_popular_services(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取热门服务列表"""
    try:
        skip = (page - 1) * size
        result = ServiceService.get_popular_services(db, skip=skip, limit=size)
        
        return success_response(
            message="获取热门服务成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/{service_id}", summary="获取服务详情")
async def get_service_detail(
    service_id: int,
    db: Session = Depends(get_db)
):
    """获取服务详细信息"""
    try:
        result = ServiceService.get_service_detail(db, service_id)
        return success_response(
            message="获取服务详情成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.put("/{service_id}", summary="更新服务信息")
async def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """更新服务信息（服务所有者）"""
    try:
        result = ServiceService.update_service(db, current_user.id, service_id, service_update)
        return success_response(
            message="服务信息更新成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.delete("/{service_id}", summary="删除服务")
async def delete_service(
    service_id: int,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """删除服务（服务所有者）"""
    try:
        result = ServiceService.delete_service(db, current_user.id, service_id)
        return success_response(
            message="服务删除成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.patch("/{service_id}/status", summary="更新服务状态")
async def update_service_status(
    service_id: int,
    status_update: ServiceStatusUpdate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """更新服务状态（服务所有者）"""
    try:
        result = ServiceService.update_service_status(db, current_user.id, service_id, status_update)
        return success_response(
            message="服务状态更新成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.patch("/{service_id}/schedule", summary="更新服务排期")
async def update_service_schedule(
    service_id: int,
    schedule_update: ServiceScheduleUpdate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """更新服务排期（服务所有者）"""
    try:
        result = ServiceService.update_service_schedule(db, current_user.id, service_id, schedule_update)
        return success_response(
            message="服务排期更新成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/{service_id}/upload-images", summary="上传服务图片")
async def upload_service_images(
    service_id: int,
    files: List[UploadFile] = File(...),
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """上传服务图片（服务所有者）"""
    try:
        result = await ServiceService.upload_service_images(db, current_user.id, service_id, files)
        return success_response(
            message="服务图片上传成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code) 
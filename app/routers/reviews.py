from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.database import get_db
from app.schemas.review import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewSearchFilter,
    ReviewStatistics, ReviewHelpful
)
from app.services.review_service import ReviewService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.dependencies import get_current_user, require_merchant

router = APIRouter()


@router.post("", summary="创建评价")
async def create_review(
    review_create: ReviewCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新评价（基于已完成订单）"""
    try:
        result = ReviewService.create_review(db, current_user.id, review_create)
        return success_response(
            message="评价创建成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/my-reviews", summary="获取我的评价")
async def get_my_reviews(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的评价列表"""
    try:
        skip = (page - 1) * size
        result = ReviewService.get_user_reviews(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["reviews"],
            total=result["total"],
            page=page,
            size=size,
            message="获取评价列表成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/merchant-reviews", summary="获取商家评价")
async def get_merchant_reviews(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取商家收到的评价列表"""
    try:
        skip = (page - 1) * size
        result = ReviewService.get_merchant_reviews(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["reviews"],
            total=result["total"],
            page=page,
            size=size,
            message="获取商家评价列表成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/service/{service_id}", summary="获取服务评价")
async def get_service_reviews(
    service_id: int,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="最低评分"),
    max_rating: Optional[int] = Query(None, ge=1, le=5, description="最高评分"),
    has_content: Optional[bool] = Query(None, description="是否有评价内容"),
    has_images: Optional[bool] = Query(None, description="是否有图片"),
    is_verified: Optional[bool] = Query(None, description="是否验证购买"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """获取服务的评价列表"""
    try:
        skip = (page - 1) * size
        
        filter_params = ReviewSearchFilter(
            service_id=service_id,
            min_rating=min_rating,
            max_rating=max_rating,
            has_content=has_content,
            has_images=has_images,
            is_verified=is_verified,
            keyword=keyword
        )
        
        result = ReviewService.get_service_reviews(
            db=db,
            service_id=service_id,
            filter_params=filter_params,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["reviews"],
            total=result["total"],
            page=page,
            size=size,
            message="获取服务评价成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/service/{service_id}/statistics", summary="获取服务评分统计")
async def get_service_rating_statistics(
    service_id: int,
    db: Session = Depends(get_db)
):
    """获取服务评分统计信息"""
    try:
        result = ReviewService.get_service_rating_statistics(db, service_id)
        return success_response(
            message="获取服务评分统计成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/merchant-statistics", summary="获取商家评分统计")
async def get_merchant_rating_statistics(
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取商家评分统计信息"""
    try:
        result = ReviewService.get_merchant_rating_statistics(db, current_user.id)
        return success_response(
            message="获取商家评分统计成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/featured", summary="获取精选评价")
async def get_featured_reviews(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取精选评价（高评分评价）"""
    try:
        skip = (page - 1) * size
        result = ReviewService.get_featured_reviews(db, skip=skip, limit=size)
        
        return success_response(
            message="获取精选评价成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/with-media", summary="获取有媒体的评价")
async def get_reviews_with_media(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取有图片或视频的评价"""
    try:
        skip = (page - 1) * size
        result = ReviewService.get_reviews_with_media(db, skip=skip, limit=size)
        
        return success_response(
            message="获取媒体评价成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/{review_id}", summary="获取评价详情")
async def get_review_detail(
    review_id: int,
    db: Session = Depends(get_db)
):
    """获取评价详细信息"""
    try:
        result = ReviewService.get_review_detail(db, review_id)
        return success_response(
            message="获取评价详情成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.put("/{review_id}", summary="更新评价信息")
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新评价信息（7天内可修改）"""
    try:
        result = ReviewService.update_review(db, current_user.id, review_id, review_update)
        return success_response(
            message="评价信息更新成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.delete("/{review_id}", summary="删除评价")
async def delete_review(
    review_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除评价"""
    try:
        result = ReviewService.delete_review(db, current_user.id, review_id)
        return success_response(
            message="评价删除成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/{review_id}/helpful", summary="标记评价有用性")
async def mark_review_helpful(
    review_id: int,
    helpful_action: ReviewHelpful,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记评价是否有用"""
    try:
        result = ReviewService.mark_helpful(db, current_user.id, review_id, helpful_action)
        return success_response(
            message="标记成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/{review_id}/upload-media", summary="上传评价媒体")
async def upload_review_media(
    review_id: int,
    files: List[UploadFile] = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传评价图片或视频"""
    try:
        result = await ReviewService.upload_review_media(db, current_user.id, review_id, files)
        return success_response(
            message="评价媒体上传成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code) 
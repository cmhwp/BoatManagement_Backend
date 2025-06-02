from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from decimal import Decimal
import json
from datetime import datetime, timedelta

from app.crud.review import crud_review
from app.crud.order import crud_order
from app.crud.service import crud_service
from app.crud.merchant import crud_merchant
from app.crud.user import crud_user
from app.schemas.review import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewListResponse,
    ReviewSearchFilter, ReviewStatistics, ReviewHelpful, ReviewModerationAction
)
from app.models.order import OrderStatus
from app.models.user import UserRole
from app.utils.logger import logger
from app.utils.file_handler import upload_image


class ReviewService:
    """评价业务逻辑类"""
    
    @staticmethod
    def create_review(db: Session, user_id: int, review_create: ReviewCreate) -> ReviewResponse:
        """创建评价"""
        # 检查用户是否存在
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查订单是否存在且属于该用户
        order = crud_order.get(db, id=review_create.order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能评价自己的订单"
            )
        
        # 检查订单状态是否已完成
        if order.status != OrderStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能评价已完成的订单"
            )
        
        # 检查是否已经评价过
        existing_review = crud_review.get_by_order(db, order_id=review_create.order_id)
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该订单已经评价过了"
            )
        
        # 确定评价对象
        service_id = review_create.service_id or order.service_id
        product_id = review_create.product_id
        
        if not service_id and not product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必须指定评价的服务或产品"
            )
        
        # 验证服务或产品是否属于订单
        if service_id and order.service_id != service_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="评价的服务与订单不匹配"
            )
        
        # 准备评价数据
        review_data = {
            "user_id": user_id,
            "order_id": review_create.order_id,
            "service_id": service_id,
            "product_id": product_id,
            "rating": review_create.rating,
            "title": review_create.title,
            "content": review_create.content,
            "service_rating": review_create.service_rating,
            "quality_rating": review_create.quality_rating,
            "value_rating": review_create.value_rating,
            "is_anonymous": review_create.is_anonymous,
            "is_verified_purchase": True  # 通过订单创建的评价都是验证购买
        }
        
        # 处理图片和视频
        if review_create.images:
            review_data["images"] = json.dumps(review_create.images, ensure_ascii=False)
        if review_create.videos:
            review_data["videos"] = json.dumps(review_create.videos, ensure_ascii=False)
        
        review = crud_review.create(db, obj_in=review_data)
        
        # 更新服务评分
        if service_id:
            ReviewService._update_service_rating(db, service_id)
        
        logger.info(f"评价创建成功: 用户{user_id}对订单{review_create.order_id}评价{review_create.rating}星")
        
        return ReviewResponse.model_validate(review)
    
    @staticmethod
    def get_user_reviews(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> dict:
        """获取用户的评价列表"""
        reviews = crud_review.get_by_user(db, user_id=user_id, skip=skip, limit=limit)
        total = crud_review.get_user_review_count(db, user_id=user_id)
        
        return {
            "reviews": [ReviewResponse.model_validate(review).model_dump() for review in reviews],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_service_reviews(
        db: Session,
        service_id: int,
        filter_params: ReviewSearchFilter,
        skip: int = 0,
        limit: int = 100
    ) -> dict:
        """获取服务的评价列表"""
        # 检查服务是否存在
        service = crud_service.get(db, id=service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务不存在"
            )
        
        if filter_params.keyword:
            reviews = crud_review.search_reviews(
                db, keyword=filter_params.keyword, skip=skip, limit=limit
            )
            # 过滤出该服务的评价
            reviews = [r for r in reviews if r.service_id == service_id]
        else:
            reviews = crud_review.get_by_service(
                db,
                service_id=service_id,
                min_rating=filter_params.min_rating,
                max_rating=filter_params.max_rating,
                has_content=filter_params.has_content,
                has_images=filter_params.has_images,
                is_verified=filter_params.is_verified,
                skip=skip,
                limit=limit
            )
        
        total = crud_review.get_service_review_count(db, service_id=service_id)
        
        return {
            "reviews": [ReviewResponse.model_validate(review).model_dump() for review in reviews],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_merchant_reviews(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> dict:
        """获取商家收到的评价列表"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能查看评价"
            )
        
        reviews = crud_review.get_merchant_reviews(
            db, merchant_id=merchant.id, skip=skip, limit=limit
        )
        
        # 简化统计（实际应该有专门的统计查询）
        all_reviews = crud_review.get_merchant_reviews(db, merchant_id=merchant.id, skip=0, limit=1000)
        total = len(all_reviews)
        
        return {
            "reviews": [ReviewResponse.model_validate(review).model_dump() for review in reviews],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_review_detail(db: Session, review_id: int) -> ReviewResponse:
        """获取评价详情"""
        review = crud_review.get(db, id=review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评价不存在"
            )
        
        if review.is_hidden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评价已被隐藏"
            )
        
        return ReviewResponse.model_validate(review)
    
    @staticmethod
    def update_review(db: Session, user_id: int, review_id: int, review_update: ReviewUpdate) -> ReviewResponse:
        """更新评价信息"""
        review = crud_review.get(db, id=review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评价不存在"
            )
        
        # 检查权限
        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改此评价"
            )
        
        # 检查评价时间限制（例如：7天内可以修改）
        if review.created_at < datetime.now() - timedelta(days=7):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="评价发布超过7天，无法修改"
            )
        
        # 处理JSON字段
        update_data = review_update.model_dump(exclude_unset=True)
        if review_update.images is not None:
            update_data["images"] = json.dumps(review_update.images, ensure_ascii=False)
        if review_update.videos is not None:
            update_data["videos"] = json.dumps(review_update.videos, ensure_ascii=False)
        
        updated_review = crud_review.update(db, db_obj=review, obj_in=update_data)
        
        # 如果评分发生变化，更新服务评分
        if review_update.rating and review.service_id:
            ReviewService._update_service_rating(db, review.service_id)
        
        logger.info(f"评价更新: 用户{user_id}更新评价{review_id}")
        
        return ReviewResponse.model_validate(updated_review)
    
    @staticmethod
    def delete_review(db: Session, user_id: int, review_id: int) -> dict:
        """删除评价"""
        review = crud_review.get(db, id=review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评价不存在"
            )
        
        # 检查权限
        user = crud_user.get(db, id=user_id)
        if review.user_id != user_id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限删除此评价"
            )
        
        service_id = review.service_id
        crud_review.remove(db, id=review_id)
        
        # 更新服务评分
        if service_id:
            ReviewService._update_service_rating(db, service_id)
        
        logger.info(f"评价删除: 用户{user_id}删除评价{review_id}")
        
        return {"message": "评价删除成功"}
    
    @staticmethod
    def mark_helpful(db: Session, user_id: int, review_id: int, helpful_action: ReviewHelpful) -> dict:
        """标记评价有用性"""
        review = crud_review.get(db, id=review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评价不存在"
            )
        
        # 简化处理：直接更新有用数（实际应该记录用户的操作避免重复）
        crud_review.update_helpful_count(db, review_id=review_id, increment=helpful_action.is_helpful)
        
        logger.info(f"评价有用性标记: 用户{user_id}标记评价{review_id}为{'有用' if helpful_action.is_helpful else '无用'}")
        
        return {"message": "操作成功"}
    
    @staticmethod
    async def upload_review_media(db: Session, user_id: int, review_id: int, files: List[UploadFile]) -> dict:
        """上传评价媒体文件"""
        review = crud_review.get(db, id=review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评价不存在"
            )
        
        # 检查权限
        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限上传此评价的媒体文件"
            )
        
        try:
            uploaded_files = []
            for file in files:
                file_info = await upload_image(file, folder="reviews")
                uploaded_files.append({
                    "url": file_info["file_url"],
                    "thumbnail": file_info.get("thumbnail_url")
                })
            
            # 更新评价图片信息
            existing_images = json.loads(review.images) if review.images else []
            existing_images.extend([f["url"] for f in uploaded_files])
            
            crud_review.update(db, db_obj=review, obj_in={"images": json.dumps(existing_images, ensure_ascii=False)})
            
            logger.info(f"评价媒体文件上传成功: 评价{review_id}, 上传 {len(files)} 个文件")
            
            return {
                "message": f"成功上传 {len(files)} 个文件",
                "files": uploaded_files
            }
        except Exception as e:
            logger.error(f"评价媒体文件上传失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="文件上传失败"
            )
    
    @staticmethod
    def get_service_rating_statistics(db: Session, service_id: int) -> ReviewStatistics:
        """获取服务评分统计"""
        # 检查服务是否存在
        service = crud_service.get(db, id=service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务不存在"
            )
        
        stats = crud_review.get_service_rating_statistics(db, service_id=service_id)
        
        # 获取最近评价数（7天内）
        recent_reviews_count = len(crud_review.get_recent_reviews(db, days=7, skip=0, limit=1000))
        recent_service_reviews = [r for r in crud_review.get_recent_reviews(db, days=7, skip=0, limit=1000) if r.service_id == service_id]
        
        return ReviewStatistics(
            total_reviews=stats["total_reviews"],
            average_rating=stats["average_rating"],
            rating_distribution=stats["rating_distribution"],
            recent_reviews=len(recent_service_reviews),
            response_rate=0.0  # 服务视角不计算回复率
        )
    
    @staticmethod
    def get_merchant_rating_statistics(db: Session, user_id: int) -> ReviewStatistics:
        """获取商家评分统计"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能查看评分统计"
            )
        
        stats = crud_review.get_merchant_rating_statistics(db, merchant_id=merchant.id)
        
        # 获取最近评价数
        recent_reviews = crud_review.get_recent_reviews(db, days=7, skip=0, limit=1000)
        merchant_recent_reviews = [r for r in recent_reviews if r.service and r.service.merchant_id == merchant.id]
        
        return ReviewStatistics(
            total_reviews=stats["total_reviews"],
            average_rating=stats["average_rating"],
            rating_distribution=stats["rating_distribution"],
            recent_reviews=len(merchant_recent_reviews),
            response_rate=stats["response_rate"]
        )
    
    @staticmethod
    def get_featured_reviews(db: Session, skip: int = 0, limit: int = 100) -> dict:
        """获取精选评价"""
        reviews = crud_review.get_top_rated_reviews(db, min_rating=4, skip=skip, limit=limit)
        
        return {
            "reviews": [ReviewResponse.model_validate(review).model_dump() for review in reviews],
            "total": len(reviews)
        }
    
    @staticmethod
    def get_reviews_with_media(db: Session, skip: int = 0, limit: int = 100) -> dict:
        """获取有媒体的评价"""
        reviews = crud_review.get_reviews_with_media(db, skip=skip, limit=limit)
        
        return {
            "reviews": [ReviewResponse.model_validate(review).model_dump() for review in reviews],
            "total": len(reviews)
        }
    
    @staticmethod
    def _update_service_rating(db: Session, service_id: int):
        """更新服务的平均评分（内部方法）"""
        stats = crud_review.get_service_rating_statistics(db, service_id=service_id)
        
        # 更新服务表中的评分字段
        service = crud_service.get(db, id=service_id)
        if service:
            crud_service.update_rating(
                db, 
                service_id=service_id, 
                new_rating=stats["average_rating"], 
                review_count=stats["total_reviews"]
            ) 
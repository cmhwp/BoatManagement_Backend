from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func, text
from datetime import datetime, timedelta
from app.crud.base import CRUDBase
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate


class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    """评价CRUD操作类"""
    
    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Review]:
        """获取用户的评价列表"""
        return db.query(Review).filter(
            Review.user_id == user_id
        ).order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
    
    def get_by_order(self, db: Session, *, order_id: int) -> Optional[Review]:
        """根据订单ID获取评价"""
        return db.query(Review).filter(Review.order_id == order_id).first()
    
    def get_by_service(
        self, 
        db: Session, 
        *, 
        service_id: int,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        has_content: Optional[bool] = None,
        has_images: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Review]:
        """获取服务的评价列表"""
        query = db.query(Review).filter(
            and_(
                Review.service_id == service_id,
                Review.is_hidden == False
            )
        )
        
        if min_rating:
            query = query.filter(Review.rating >= min_rating)
        
        if max_rating:
            query = query.filter(Review.rating <= max_rating)
        
        if has_content is not None:
            if has_content:
                query = query.filter(Review.content.isnot(None), Review.content != "")
            else:
                query = query.filter(or_(Review.content.is_(None), Review.content == ""))
        
        if has_images is not None:
            if has_images:
                query = query.filter(Review.images.isnot(None), Review.images != "")
            else:
                query = query.filter(or_(Review.images.is_(None), Review.images == ""))
        
        if is_verified is not None:
            query = query.filter(Review.is_verified_purchase == is_verified)
        
        return query.order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
    
    def get_by_product(
        self, 
        db: Session, 
        *, 
        product_id: int,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Review]:
        """获取产品的评价列表"""
        query = db.query(Review).filter(
            and_(
                Review.product_id == product_id,
                Review.is_hidden == False
            )
        )
        
        if min_rating:
            query = query.filter(Review.rating >= min_rating)
        
        if max_rating:
            query = query.filter(Review.rating <= max_rating)
        
        return query.order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
    
    def get_merchant_reviews(
        self, 
        db: Session, 
        *, 
        merchant_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Review]:
        """获取商家收到的评价列表（通过服务关联）"""
        return db.query(Review).join(Review.service).filter(
            and_(
                Review.service.has(merchant_id=merchant_id),
                Review.is_hidden == False
            )
        ).order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
    
    def get_recent_reviews(
        self, 
        db: Session, 
        *, 
        days: int = 7,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Review]:
        """获取最近的评价"""
        since_date = datetime.now() - timedelta(days=days)
        return db.query(Review).filter(
            and_(
                Review.created_at >= since_date,
                Review.is_hidden == False
            )
        ).order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
    
    def get_top_rated_reviews(
        self, 
        db: Session, 
        *, 
        min_rating: int = 4,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Review]:
        """获取高评分评价"""
        return db.query(Review).filter(
            and_(
                Review.rating >= min_rating,
                Review.is_hidden == False
            )
        ).order_by(desc(Review.rating), desc(Review.helpful_count)).offset(skip).limit(limit).all()
    
    def get_reviews_with_media(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Review]:
        """获取有图片或视频的评价"""
        return db.query(Review).filter(
            and_(
                or_(
                    and_(Review.images.isnot(None), Review.images != ""),
                    and_(Review.videos.isnot(None), Review.videos != "")
                ),
                Review.is_hidden == False
            )
        ).order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
    
    def search_reviews(
        self,
        db: Session,
        *,
        keyword: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """搜索评价"""
        return self.search(
            db,
            keyword=keyword,
            search_fields=["title", "content"],
            additional_filters=[Review.is_hidden == False],
            skip=skip,
            limit=limit
        )
    
    def get_service_rating_statistics(self, db: Session, *, service_id: int) -> dict:
        """获取服务评分统计"""
        reviews = db.query(Review).filter(
            and_(
                Review.service_id == service_id,
                Review.is_hidden == False
            )
        ).all()
        
        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0.0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        total_reviews = len(reviews)
        average_rating = sum([r.rating for r in reviews]) / total_reviews
        
        # 评分分布
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_distribution[review.rating] += 1
        
        return {
            "total_reviews": total_reviews,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution
        }
    
    def get_merchant_rating_statistics(self, db: Session, *, merchant_id: int) -> dict:
        """获取商家评分统计"""
        reviews = db.query(Review).join(Review.service).filter(
            and_(
                Review.service.has(merchant_id=merchant_id),
                Review.is_hidden == False
            )
        ).all()
        
        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0.0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "response_rate": 0.0
            }
        
        total_reviews = len(reviews)
        average_rating = sum([r.rating for r in reviews]) / total_reviews
        
        # 评分分布
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_distribution[review.rating] += 1
        
        # 回复率（假设reply_count > 0表示有回复）
        replied_reviews = len([r for r in reviews if r.reply_count > 0])
        response_rate = (replied_reviews / total_reviews) * 100 if total_reviews > 0 else 0
        
        return {
            "total_reviews": total_reviews,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution,
            "response_rate": round(response_rate, 2)
        }
    
    def get_user_review_count(self, db: Session, *, user_id: int) -> int:
        """获取用户评价总数"""
        return db.query(Review).filter(Review.user_id == user_id).count()
    
    def get_service_review_count(self, db: Session, *, service_id: int) -> int:
        """获取服务评价总数"""
        return db.query(Review).filter(
            and_(
                Review.service_id == service_id,
                Review.is_hidden == False
            )
        ).count()
    
    def update_helpful_count(self, db: Session, *, review_id: int, increment: bool = True) -> Optional[Review]:
        """更新评价有用数"""
        review = self.get(db, id=review_id)
        if review:
            current_count = review.helpful_count or 0
            new_count = current_count + 1 if increment else max(0, current_count - 1)
            review = self.update(db, db_obj=review, obj_in={"helpful_count": new_count})
        return review
    
    def update_reply_count(self, db: Session, *, review_id: int, increment: bool = True) -> Optional[Review]:
        """更新评价回复数"""
        review = self.get(db, id=review_id)
        if review:
            current_count = review.reply_count or 0
            new_count = current_count + 1 if increment else max(0, current_count - 1)
            review = self.update(db, db_obj=review, obj_in={"reply_count": new_count})
        return review
    
    def hide_review(self, db: Session, *, review_id: int, admin_notes: Optional[str] = None) -> Optional[Review]:
        """隐藏评价"""
        review = self.get(db, id=review_id)
        if review:
            update_data = {"is_hidden": True}
            if admin_notes:
                update_data["admin_notes"] = admin_notes
            review = self.update(db, db_obj=review, obj_in=update_data)
        return review
    
    def show_review(self, db: Session, *, review_id: int) -> Optional[Review]:
        """显示评价"""
        review = self.get(db, id=review_id)
        if review:
            review = self.update(db, db_obj=review, obj_in={"is_hidden": False})
        return review
    
    def get_pending_reviews(self, db: Session, *, limit: int = 100) -> List[Review]:
        """获取待审核的评价（可能包含敏感内容）"""
        # 这里可以添加关键词检测或其他审核逻辑
        return db.query(Review).filter(
            Review.is_hidden == False
        ).order_by(desc(Review.created_at)).limit(limit).all()


# 创建CRUD实例
crud_review = CRUDReview(Review) 
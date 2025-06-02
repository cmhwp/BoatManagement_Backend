from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.crud.base import CRUDBase
from app.models.service import Service, ServiceStatus, ServiceType
from app.schemas.service import ServiceCreate, ServiceUpdate


class CRUDService(CRUDBase[Service, ServiceCreate, ServiceUpdate]):
    """服务CRUD操作类"""
    
    def get_by_merchant(self, db: Session, *, merchant_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
        """获取商家的服务列表"""
        return db.query(Service).filter(
            Service.merchant_id == merchant_id
        ).offset(skip).limit(limit).all()
    
    def get_by_boat(self, db: Session, *, boat_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
        """获取指定船艇的服务列表"""
        return db.query(Service).filter(
            Service.boat_id == boat_id
        ).offset(skip).limit(limit).all()
    
    def get_active_services(
        self, 
        db: Session, 
        *, 
        service_type: Optional[ServiceType] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        max_participants: Optional[int] = None,
        region_id: Optional[int] = None,
        is_green_service: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Service]:
        """获取可预订服务列表（带筛选条件）"""
        query = db.query(Service).filter(Service.status == ServiceStatus.ACTIVE)
        
        if service_type:
            query = query.filter(Service.service_type == service_type)
        
        if min_price:
            query = query.filter(Service.price >= min_price)
        
        if max_price:
            query = query.filter(Service.price <= max_price)
        
        if max_participants:
            query = query.filter(Service.max_participants >= max_participants)
        
        if region_id:
            query = query.filter(Service.region_id == region_id)
        
        if is_green_service is not None:
            query = query.filter(Service.is_green_service == is_green_service)
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, *, status: ServiceStatus, skip: int = 0, limit: int = 100) -> List[Service]:
        """根据状态获取服务列表"""
        return db.query(Service).filter(
            Service.status == status
        ).offset(skip).limit(limit).all()
    
    def get_featured_services(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Service]:
        """获取推荐服务"""
        return db.query(Service).filter(
            and_(
                Service.is_featured == True,
                Service.status == ServiceStatus.ACTIVE
            )
        ).order_by(Service.rating.desc(), Service.booking_count.desc()).offset(skip).limit(limit).all()
    
    def get_green_services(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Service]:
        """获取绿色服务"""
        return db.query(Service).filter(
            and_(
                Service.is_green_service == True,
                Service.status == ServiceStatus.ACTIVE
            )
        ).offset(skip).limit(limit).all()
    
    def get_popular_services(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Service]:
        """获取热门服务（按预订次数排序）"""
        return db.query(Service).filter(
            Service.status == ServiceStatus.ACTIVE
        ).order_by(Service.booking_count.desc()).offset(skip).limit(limit).all()
    
    def get_highly_rated_services(self, db: Session, *, min_rating: float = 4.0, skip: int = 0, limit: int = 100) -> List[Service]:
        """获取高评分服务"""
        return db.query(Service).filter(
            and_(
                Service.status == ServiceStatus.ACTIVE,
                Service.rating >= min_rating,
                Service.review_count >= 5  # 至少有5个评价
            )
        ).order_by(Service.rating.desc()).offset(skip).limit(limit).all()
    
    def search_services(
        self,
        db: Session,
        *,
        keyword: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Service]:
        """搜索服务"""
        return self.search(
            db,
            keyword=keyword,
            search_fields=["title", "description", "meeting_point"],
            skip=skip,
            limit=limit
        )
    
    def get_services_by_region(self, db: Session, *, region_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
        """根据地区获取服务"""
        return db.query(Service).filter(
            and_(
                Service.region_id == region_id,
                Service.status == ServiceStatus.ACTIVE
            )
        ).offset(skip).limit(limit).all()
    
    def get_merchant_service_count(self, db: Session, *, merchant_id: int) -> int:
        """获取商家服务数量"""
        return db.query(Service).filter(Service.merchant_id == merchant_id).count()
    
    def get_active_service_count(self, db: Session, *, merchant_id: int) -> int:
        """获取商家可预订服务数量"""
        return db.query(Service).filter(
            and_(
                Service.merchant_id == merchant_id,
                Service.status == ServiceStatus.ACTIVE
            )
        ).count()
    
    def update_status(self, db: Session, *, service_id: int, status: ServiceStatus) -> Optional[Service]:
        """更新服务状态"""
        service = self.get(db, id=service_id)
        if service:
            service = self.update(db, db_obj=service, obj_in={"status": status})
        return service
    
    def update_rating(self, db: Session, *, service_id: int, new_rating: float, review_count: int) -> Optional[Service]:
        """更新服务评分"""
        service = self.get(db, id=service_id)
        if service:
            service = self.update(db, db_obj=service, obj_in={
                "rating": new_rating,
                "review_count": review_count
            })
        return service
    
    def increment_booking_count(self, db: Session, *, service_id: int) -> Optional[Service]:
        """增加预订次数"""
        service = self.get(db, id=service_id)
        if service:
            service = self.update(db, db_obj=service, obj_in={
                "booking_count": service.booking_count + 1
            })
        return service


# 创建CRUD实例
crud_service = CRUDService(Service) 
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.crud.base import CRUDBase
from app.models.boat import Boat, BoatStatus, BoatType
from app.schemas.boat import BoatCreate, BoatUpdate


class CRUDBoat(CRUDBase[Boat, BoatCreate, BoatUpdate]):
    """船艇CRUD操作类"""
    
    def get_by_merchant(self, db: Session, *, merchant_id: int, skip: int = 0, limit: int = 100) -> List[Boat]:
        """获取商家的船艇列表"""
        return db.query(Boat).filter(
            Boat.merchant_id == merchant_id
        ).offset(skip).limit(limit).all()
    
    def get_by_registration_number(self, db: Session, *, registration_number: str) -> Optional[Boat]:
        """根据船舶登记号获取船艇"""
        return db.query(Boat).filter(
            Boat.registration_number == registration_number
        ).first()
    
    def get_available_boats(
        self, 
        db: Session, 
        *, 
        boat_type: Optional[BoatType] = None,
        min_capacity: Optional[int] = None,
        max_hourly_rate: Optional[float] = None,
        location: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Boat]:
        """获取可用船艇列表（带筛选条件）"""
        query = db.query(Boat).filter(Boat.status == BoatStatus.AVAILABLE)
        
        if boat_type:
            query = query.filter(Boat.boat_type == boat_type)
        
        if min_capacity:
            query = query.filter(Boat.max_capacity >= min_capacity)
        
        if max_hourly_rate:
            query = query.filter(
                or_(
                    Boat.hourly_rate <= max_hourly_rate,
                    Boat.hourly_rate.is_(None)
                )
            )
        
        if location:
            query = query.filter(
                or_(
                    Boat.home_port.ilike(f"%{location}%"),
                    Boat.current_location.ilike(f"%{location}%")
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, *, status: BoatStatus, skip: int = 0, limit: int = 100) -> List[Boat]:
        """根据状态获取船艇列表"""
        return db.query(Boat).filter(
            Boat.status == status
        ).offset(skip).limit(limit).all()
    
    def get_boats_need_maintenance(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Boat]:
        """获取需要维护的船艇"""
        from datetime import datetime
        today = datetime.now()
        
        return db.query(Boat).filter(
            and_(
                Boat.next_maintenance <= today,
                Boat.status != BoatStatus.MAINTENANCE,
                Boat.status != BoatStatus.RETIRED
            )
        ).offset(skip).limit(limit).all()
    
    def get_green_certified_boats(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Boat]:
        """获取绿色认证船艇"""
        return db.query(Boat).filter(
            and_(
                Boat.is_green_certified == True,
                Boat.status == BoatStatus.AVAILABLE
            )
        ).offset(skip).limit(limit).all()
    
    def search_boats(
        self,
        db: Session,
        *,
        keyword: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Boat]:
        """搜索船艇"""
        return self.search(
            db,
            keyword=keyword,
            search_fields=["name", "model", "manufacturer", "home_port"],
            skip=skip,
            limit=limit
        )
    
    def get_merchant_boat_count(self, db: Session, *, merchant_id: int) -> int:
        """获取商家船艇数量"""
        return db.query(Boat).filter(Boat.merchant_id == merchant_id).count()
    
    def get_available_boat_count(self, db: Session, *, merchant_id: int) -> int:
        """获取商家可用船艇数量"""
        return db.query(Boat).filter(
            and_(
                Boat.merchant_id == merchant_id,
                Boat.status == BoatStatus.AVAILABLE
            )
        ).count()
    
    def update_status(self, db: Session, *, boat_id: int, status: BoatStatus, notes: Optional[str] = None) -> Optional[Boat]:
        """更新船艇状态"""
        boat = self.get(db, id=boat_id)
        if boat:
            update_data = {"status": status}
            if notes and status == BoatStatus.MAINTENANCE:
                update_data["maintenance_notes"] = notes
            
            boat = self.update(db, db_obj=boat, obj_in=update_data)
        return boat
    
    def update_location(self, db: Session, *, boat_id: int, location: str, gps_coordinates: Optional[str] = None) -> Optional[Boat]:
        """更新船艇位置"""
        boat = self.get(db, id=boat_id)
        if boat:
            update_data = {"current_location": location}
            if gps_coordinates:
                update_data["gps_coordinates"] = gps_coordinates
            
            boat = self.update(db, db_obj=boat, obj_in=update_data)
        return boat


# 创建CRUD实例
crud_boat = CRUDBoat(Boat) 
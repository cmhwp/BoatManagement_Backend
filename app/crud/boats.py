from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.boats import Boat, BoatStatus
from app.schemas.boats import BoatCreate, BoatUpdate


def get_boat(db: Session, boat_id: int) -> Optional[Boat]:
    """根据ID获取船艇"""
    return db.query(Boat).filter(Boat.boat_id == boat_id).first()


def get_boat_by_gps(db: Session, gps_id: str) -> Optional[Boat]:
    """根据GPS设备ID获取船艇"""
    return db.query(Boat).filter(Boat.gps_id == gps_id).first()


def get_merchant_boats(db: Session, merchant_id: int) -> List[Boat]:
    """获取商家的船艇列表"""
    return db.query(Boat).filter(Boat.merchant_id == merchant_id).all()


def get_available_boats(db: Session, merchant_id: int = None) -> List[Boat]:
    """获取可用船艇列表"""
    query = db.query(Boat).filter(Boat.status == BoatStatus.free)
    if merchant_id:
        query = query.filter(Boat.merchant_id == merchant_id)
    return query.all()


def get_boats(db: Session, skip: int = 0, limit: int = 100) -> List[Boat]:
    """获取船艇列表"""
    return db.query(Boat).offset(skip).limit(limit).all()


def create_boat(db: Session, boat: BoatCreate) -> Boat:
    """创建船艇"""
    db_boat = Boat(
        merchant_id=boat.merchant_id,
        boat_name=boat.boat_name,
        boat_type=boat.boat_type,
        capacity=boat.capacity,
        gps_id=boat.gps_id
    )
    db.add(db_boat)
    db.commit()
    db.refresh(db_boat)
    return db_boat


def update_boat(db: Session, boat_id: int, boat_update: BoatUpdate) -> Optional[Boat]:
    """更新船艇信息"""
    db_boat = get_boat(db, boat_id)
    if db_boat:
        update_data = boat_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_boat, field, value)
        db.commit()
        db.refresh(db_boat)
    return db_boat


def update_boat_status(db: Session, boat_id: int, status: BoatStatus) -> Optional[Boat]:
    """更新船艇状态"""
    db_boat = get_boat(db, boat_id)
    if db_boat:
        db_boat.status = status
        db.commit()
        db.refresh(db_boat)
    return db_boat


def delete_boat(db: Session, boat_id: int) -> bool:
    """删除船艇"""
    db_boat = get_boat(db, boat_id)
    if db_boat:
        db.delete(db_boat)
        db.commit()
        return True
    return False 
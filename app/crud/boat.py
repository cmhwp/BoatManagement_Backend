from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from app.models.boat import Boat
from app.models.enums import BoatStatus, BoatType
from app.schemas.boat import BoatCreate, BoatUpdate
from app.schemas.common import PaginationParams


def create_boat(db: Session, boat: BoatCreate) -> Boat:
    """创建船艇"""
    db_boat = Boat(
        merchant_id=boat.merchant_id,
        name=boat.name,
        boat_type=boat.boat_type,
        registration_no=boat.registration_no,
        license_no=boat.license_no,
        length=boat.length,
        width=boat.width,
        passenger_capacity=boat.passenger_capacity,
        engine_power=boat.engine_power,
        current_location=boat.current_location,
        safety_equipment=boat.safety_equipment,
        insurance_no=boat.insurance_no,
        insurance_expiry=boat.insurance_expiry,
        daily_rate=boat.daily_rate,
        hourly_rate=boat.hourly_rate,
        description=boat.description,
        images=boat.images
    )
    db.add(db_boat)
    db.commit()
    db.refresh(db_boat)
    return db_boat


def get_boat_by_id(db: Session, boat_id: int) -> Optional[Boat]:
    """根据ID获取船艇"""
    return db.query(Boat).filter(Boat.id == boat_id).first()


def get_boat_by_registration_no(db: Session, registration_no: str) -> Optional[Boat]:
    """根据注册编号获取船艇"""
    return db.query(Boat).filter(Boat.registration_no == registration_no).first()


def get_boats(
    db: Session, 
    pagination: PaginationParams,
    merchant_id: Optional[int] = None,
    boat_type: Optional[BoatType] = None,
    status: Optional[BoatStatus] = None,
    is_available: Optional[bool] = None,
    min_capacity: Optional[int] = None,
    search: Optional[str] = None
) -> tuple[List[Boat], int]:
    """获取船艇列表"""
    query = db.query(Boat)
    
    # 应用过滤条件
    if merchant_id:
        query = query.filter(Boat.merchant_id == merchant_id)
    
    if boat_type:
        query = query.filter(Boat.boat_type == boat_type)
    
    if status:
        query = query.filter(Boat.status == status)
    
    if is_available is not None:
        query = query.filter(Boat.is_available == is_available)
    
    if min_capacity:
        query = query.filter(Boat.passenger_capacity >= min_capacity)
    
    if search:
        query = query.filter(
            or_(
                Boat.name.contains(search),
                Boat.registration_no.contains(search),
                Boat.current_location.contains(search)
            )
        )
    
    # 获取总数
    total = query.count()
    
    # 应用分页
    boats = query.offset(pagination.get_offset()).limit(pagination.get_limit()).all()
    
    return boats, total


def get_available_boats(
    db: Session, 
    pagination: PaginationParams,
    boat_type: Optional[BoatType] = None,
    min_capacity: Optional[int] = None,
    location: Optional[str] = None
) -> tuple[List[Boat], int]:
    """获取可用船艇列表"""
    query = db.query(Boat).filter(
        and_(
            Boat.is_available == True,
            Boat.status == BoatStatus.AVAILABLE
        )
    )
    
    if boat_type:
        query = query.filter(Boat.boat_type == boat_type)
    
    if min_capacity:
        query = query.filter(Boat.passenger_capacity >= min_capacity)
    
    if location:
        query = query.filter(Boat.current_location.contains(location))
    
    # 按日租金升序排列
    query = query.order_by(Boat.daily_rate.asc())
    
    total = query.count()
    boats = query.offset(pagination.get_offset()).limit(pagination.get_limit()).all()
    
    return boats, total


def get_merchant_boats(
    db: Session,
    merchant_id: int,
    pagination: PaginationParams,
    status: Optional[BoatStatus] = None
) -> tuple[List[Boat], int]:
    """获取商家的船艇列表"""
    query = db.query(Boat).filter(Boat.merchant_id == merchant_id)
    
    if status:
        query = query.filter(Boat.status == status)
    
    total = query.count()
    boats = query.offset(pagination.get_offset()).limit(pagination.get_limit()).all()
    
    return boats, total


def update_boat(db: Session, boat_id: int, boat_update: BoatUpdate) -> Optional[Boat]:
    """更新船艇信息"""
    db_boat = get_boat_by_id(db, boat_id)
    if not db_boat:
        return None
    
    update_data = boat_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_boat, field, value)
    
    db.commit()
    db.refresh(db_boat)
    return db_boat


def update_boat_status(
    db: Session, 
    boat_id: int, 
    status: BoatStatus, 
    is_available: bool,
    current_location: Optional[str] = None
) -> Optional[Boat]:
    """更新船艇状态"""
    db_boat = get_boat_by_id(db, boat_id)
    if not db_boat:
        return None
    
    db_boat.status = status
    db_boat.is_available = is_available
    
    if current_location:
        db_boat.current_location = current_location
    
    db.commit()
    db.refresh(db_boat)
    return db_boat


def update_boat_location(db: Session, boat_id: int, location: str) -> Optional[Boat]:
    """更新船艇位置"""
    db_boat = get_boat_by_id(db, boat_id)
    if not db_boat:
        return None
    
    db_boat.current_location = location
    
    db.commit()
    db.refresh(db_boat)
    return db_boat


def delete_boat(db: Session, boat_id: int) -> bool:
    """删除船艇"""
    db_boat = get_boat_by_id(db, boat_id)
    if not db_boat:
        return False
    
    db.delete(db_boat)
    db.commit()
    return True 
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from app.models.crew_info import CrewInfo
from app.schemas.crew import CrewCreate, CrewUpdate
from app.schemas.common import PaginationParams


def create_crew(db: Session, crew: CrewCreate) -> CrewInfo:
    """创建船员"""
    db_crew = CrewInfo(
        user_id=crew.user_id,
        id_card_no=crew.id_card_no,
        license_no=crew.license_no,
        license_type=crew.license_type,
        license_expiry=crew.license_expiry,
        years_of_experience=crew.years_of_experience,
        specialties=crew.specialties,
        emergency_contact=crew.emergency_contact,
        emergency_phone=crew.emergency_phone
    )
    db.add(db_crew)
    db.commit()
    db.refresh(db_crew)
    return db_crew


def get_crew_by_id(db: Session, crew_id: int) -> Optional[CrewInfo]:
    """根据ID获取船员"""
    return db.query(CrewInfo).filter(CrewInfo.id == crew_id).first()


def get_crew_by_user_id(db: Session, user_id: int) -> Optional[CrewInfo]:
    """根据用户ID获取船员"""
    return db.query(CrewInfo).filter(CrewInfo.user_id == user_id).first()


def get_crew_by_id_card_no(db: Session, id_card_no: str) -> Optional[CrewInfo]:
    """根据身份证号获取船员"""
    return db.query(CrewInfo).filter(CrewInfo.id_card_no == id_card_no).first()


def get_crew_by_license_no(db: Session, license_no: str) -> Optional[CrewInfo]:
    """根据证书号获取船员"""
    return db.query(CrewInfo).filter(CrewInfo.license_no == license_no).first()


def get_crews(
    db: Session, 
    pagination: PaginationParams,
    is_available: Optional[bool] = None,
    license_type: Optional[str] = None,
    min_experience: Optional[int] = None,
    search: Optional[str] = None
) -> tuple[List[CrewInfo], int]:
    """获取船员列表"""
    query = db.query(CrewInfo)
    
    # 应用过滤条件
    if is_available is not None:
        query = query.filter(CrewInfo.is_available == is_available)
    
    if license_type:
        query = query.filter(CrewInfo.license_type == license_type)
    
    if min_experience is not None:
        query = query.filter(CrewInfo.years_of_experience >= min_experience)
    
    if search:
        query = query.filter(
            or_(
                CrewInfo.license_no.contains(search),
                CrewInfo.emergency_contact.contains(search)
            )
        )
    
    # 获取总数
    total = query.count()
    
    # 应用分页
    crews = query.offset(pagination.get_offset()).limit(pagination.get_limit()).all()
    
    return crews, total


def get_available_crews(
    db: Session, 
    pagination: PaginationParams,
    license_type: Optional[str] = None
) -> tuple[List[CrewInfo], int]:
    """获取可用船员列表"""
    query = db.query(CrewInfo).filter(
        and_(
            CrewInfo.is_available == True,
            CrewInfo.current_status == "available"
        )
    )
    
    if license_type:
        query = query.filter(CrewInfo.license_type == license_type)
    
    # 按评分降序排列
    query = query.order_by(CrewInfo.rating.desc())
    
    total = query.count()
    crews = query.offset(pagination.get_offset()).limit(pagination.get_limit()).all()
    
    return crews, total


def update_crew(db: Session, crew_id: int, crew_update: CrewUpdate) -> Optional[CrewInfo]:
    """更新船员信息"""
    db_crew = get_crew_by_id(db, crew_id)
    if not db_crew:
        return None
    
    update_data = crew_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_crew, field, value)
    
    db.commit()
    db.refresh(db_crew)
    return db_crew


def update_crew_status(db: Session, crew_id: int, is_available: bool, current_status: str) -> Optional[CrewInfo]:
    """更新船员状态"""
    db_crew = get_crew_by_id(db, crew_id)
    if not db_crew:
        return None
    
    db_crew.is_available = is_available
    db_crew.current_status = current_status
    
    db.commit()
    db.refresh(db_crew)
    return db_crew


def update_crew_rating(db: Session, crew_id: int, new_rating: float) -> Optional[CrewInfo]:
    """更新船员评分"""
    db_crew = get_crew_by_id(db, crew_id)
    if not db_crew:
        return None
    
    db_crew.rating = new_rating
    db_crew.total_services += 1
    
    db.commit()
    db.refresh(db_crew)
    return db_crew


def delete_crew(db: Session, crew_id: int) -> bool:
    """删除船员"""
    db_crew = get_crew_by_id(db, crew_id)
    if not db_crew:
        return False
    
    db.delete(db_crew)
    db.commit()
    return True 
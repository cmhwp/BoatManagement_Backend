from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.merchants import Merchant
from app.models.crew_info import CrewInfo
from app.schemas.merchants import MerchantCreate, MerchantUpdate, CrewInfoCreate, CrewInfoUpdate
from datetime import datetime


def get_merchant(db: Session, merchant_id: int) -> Optional[Merchant]:
    """根据ID获取商家"""
    return db.query(Merchant).filter(Merchant.merchant_id == merchant_id).first()


def get_merchant_by_user_id(db: Session, user_id: int) -> Optional[Merchant]:
    """根据用户ID获取商家"""
    return db.query(Merchant).filter(Merchant.user_id == user_id).first()


def get_merchant_by_license(db: Session, license_no: str) -> Optional[Merchant]:
    """根据营业执照号获取商家"""
    return db.query(Merchant).filter(Merchant.license_no == license_no).first()


def get_merchants(db: Session, skip: int = 0, limit: int = 100) -> List[Merchant]:
    """获取商家列表"""
    return db.query(Merchant).offset(skip).limit(limit).all()


def create_merchant(db: Session, user_id: int, merchant: MerchantCreate) -> Merchant:
    """创建商家"""
    db_merchant = Merchant(
        user_id=user_id,
        business_name=merchant.business_name,
        license_no=merchant.license_no,
        contact_person=merchant.contact_person,
        business_type=merchant.business_type
    )
    db.add(db_merchant)
    db.commit()
    db.refresh(db_merchant)
    return db_merchant


def update_merchant(db: Session, merchant_id: int, merchant_update: MerchantUpdate) -> Optional[Merchant]:
    """更新商家信息"""
    db_merchant = get_merchant(db, merchant_id)
    if db_merchant:
        update_data = merchant_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_merchant, field, value)
        db_merchant.update_time = datetime.utcnow()
        db.commit()
        db.refresh(db_merchant)
    return db_merchant


def delete_merchant(db: Session, merchant_id: int) -> bool:
    """删除商家"""
    db_merchant = get_merchant(db, merchant_id)
    if db_merchant:
        db.delete(db_merchant)
        db.commit()
        return True
    return False


# 船员相关CRUD

def get_crew(db: Session, crew_id: int) -> Optional[CrewInfo]:
    """根据ID获取船员"""
    return db.query(CrewInfo).filter(CrewInfo.crew_id == crew_id).first()


def get_crew_by_user_id(db: Session, user_id: int) -> Optional[CrewInfo]:
    """根据用户ID获取船员"""
    return db.query(CrewInfo).filter(CrewInfo.user_id == user_id).first()


def get_crew_by_certificate(db: Session, certificate_id: str) -> Optional[CrewInfo]:
    """根据证书号获取船员"""
    return db.query(CrewInfo).filter(CrewInfo.certificate_id == certificate_id).first()


def get_merchant_crews(db: Session, merchant_id: int) -> List[CrewInfo]:
    """获取商家的船员列表"""
    return db.query(CrewInfo).filter(CrewInfo.merchant_id == merchant_id).all()


def create_crew(db: Session, user_id: int, crew: CrewInfoCreate) -> CrewInfo:
    """创建船员"""
    db_crew = CrewInfo(
        user_id=user_id,
        merchant_id=crew.merchant_id,
        certificate_id=crew.certificate_id,
        boat_type=crew.boat_type
    )
    db.add(db_crew)
    db.commit()
    db.refresh(db_crew)
    return db_crew


def update_crew(db: Session, crew_id: int, crew_update: CrewInfoUpdate) -> Optional[CrewInfo]:
    """更新船员信息"""
    db_crew = get_crew(db, crew_id)
    if db_crew:
        update_data = crew_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_crew, field, value)
        db_crew.update_time = datetime.utcnow()
        db.commit()
        db.refresh(db_crew)
    return db_crew


def delete_crew(db: Session, crew_id: int) -> bool:
    """删除船员"""
    db_crew = get_crew(db, crew_id)
    if db_crew:
        db.delete(db_crew)
        db.commit()
        return True
    return False 
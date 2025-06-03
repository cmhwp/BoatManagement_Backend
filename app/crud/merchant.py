from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate, MerchantUpdate
from app.schemas.common import PaginationParams


def create_merchant(db: Session, merchant: MerchantCreate) -> Merchant:
    """创建商家"""
    db_merchant = Merchant(
        user_id=merchant.user_id,
        company_name=merchant.company_name,
        business_license_no=merchant.business_license_no,
        legal_representative=merchant.legal_representative,
        registration_address=merchant.registration_address,
        business_address=merchant.business_address,
        contact_person=merchant.contact_person,
        contact_phone=merchant.contact_phone,
        contact_email=merchant.contact_email
    )
    db.add(db_merchant)
    db.commit()
    db.refresh(db_merchant)
    return db_merchant


def get_merchant_by_id(db: Session, merchant_id: int) -> Optional[Merchant]:
    """根据ID获取商家"""
    return db.query(Merchant).filter(Merchant.id == merchant_id).first()


def get_merchant_by_user_id(db: Session, user_id: int) -> Optional[Merchant]:
    """根据用户ID获取商家"""
    return db.query(Merchant).filter(Merchant.user_id == user_id).first()


def get_merchant_by_license_no(db: Session, license_no: str) -> Optional[Merchant]:
    """根据营业执照号获取商家"""
    return db.query(Merchant).filter(Merchant.business_license_no == license_no).first()


def get_merchants(
    db: Session, 
    pagination: PaginationParams,
    is_verified: Optional[bool] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> tuple[List[Merchant], int]:
    """获取商家列表"""
    query = db.query(Merchant)
    
    # 应用过滤条件
    if is_verified is not None:
        query = query.filter(Merchant.is_verified == is_verified)
    
    if is_active is not None:
        query = query.filter(Merchant.is_active == is_active)
    
    if search:
        query = query.filter(
            or_(
                Merchant.company_name.contains(search),
                Merchant.contact_person.contains(search)
            )
        )
    
    # 获取总数
    total = query.count()
    
    # 应用分页
    merchants = query.offset(pagination.get_offset()).limit(pagination.get_limit()).all()
    
    return merchants, total


def update_merchant(db: Session, merchant_id: int, merchant_update: MerchantUpdate) -> Optional[Merchant]:
    """更新商家信息"""
    db_merchant = get_merchant_by_id(db, merchant_id)
    if not db_merchant:
        return None
    
    update_data = merchant_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_merchant, field, value)
    
    db.commit()
    db.refresh(db_merchant)
    return db_merchant


def verify_merchant(db: Session, merchant_id: int, is_verified: bool) -> Optional[Merchant]:
    """验证商家"""
    db_merchant = get_merchant_by_id(db, merchant_id)
    if not db_merchant:
        return None
    
    db_merchant.is_verified = is_verified
    if is_verified:
        db_merchant.verification_date = func.now()
    
    db.commit()
    db.refresh(db_merchant)
    return db_merchant


def activate_merchant(db: Session, merchant_id: int, is_active: bool) -> Optional[Merchant]:
    """激活/停用商家"""
    db_merchant = get_merchant_by_id(db, merchant_id)
    if not db_merchant:
        return None
    
    db_merchant.is_active = is_active
    
    db.commit()
    db.refresh(db_merchant)
    return db_merchant


def delete_merchant(db: Session, merchant_id: int) -> bool:
    """删除商家"""
    db_merchant = get_merchant_by_id(db, merchant_id)
    if not db_merchant:
        return False
    
    db.delete(db_merchant)
    db.commit()
    return True 
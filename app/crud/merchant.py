from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate, MerchantUpdate


class CRUDMerchant(CRUDBase[Merchant, MerchantCreate, MerchantUpdate]):
    """商家CRUD操作类"""
    
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[Merchant]:
        """根据用户ID获取商家信息"""
        return db.query(Merchant).filter(Merchant.user_id == user_id).first()
    
    def get_by_business_license(self, db: Session, *, business_license: str) -> Optional[Merchant]:
        """根据营业执照号获取商家"""
        return db.query(Merchant).filter(Merchant.business_license == business_license).first()
    
    def get_verified_merchants(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Merchant]:
        """获取已认证的商家列表"""
        from app.models.merchant import MerchantStatus
        return db.query(Merchant).filter(
            Merchant.status == MerchantStatus.ACTIVE
        ).offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, *, status: str, skip: int = 0, limit: int = 100) -> List[Merchant]:
        """根据状态获取商家列表"""
        return db.query(Merchant).filter(
            Merchant.status == status
        ).offset(skip).limit(limit).all()
    
    def search_merchants(
        self,
        db: Session,
        *,
        keyword: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Merchant]:
        """搜索商家"""
        return self.search(
            db,
            keyword=keyword,
            search_fields=["business_name", "business_scope", "business_address"],
            skip=skip,
            limit=limit
        )
    
    def get_merchants_by_location(
        self,
        db: Session,
        *,
        latitude: float,
        longitude: float,
        radius: float = 10.0,  # 半径10公里
        skip: int = 0,
        limit: int = 100
    ) -> List[Merchant]:
        """根据地理位置获取附近商家"""
        from sqlalchemy import func
        from app.models.merchant import MerchantStatus
        
        # 简化的距离计算（实际项目中应该使用更精确的地理距离计算）
        return db.query(Merchant).filter(
            Merchant.status == MerchantStatus.ACTIVE,
            Merchant.location_latitude.isnot(None),
            Merchant.location_longitude.isnot(None),
            func.abs(Merchant.location_latitude - latitude) <= radius / 111.0,  # 粗略计算
            func.abs(Merchant.location_longitude - longitude) <= radius / 111.0
        ).offset(skip).limit(limit).all()
    
    def update_rating(self, db: Session, *, merchant_id: int, new_rating: float) -> Optional[Merchant]:
        """更新商家评分"""
        merchant = self.get(db, id=merchant_id)
        if merchant:
            merchant.rating = new_rating
            db.add(merchant)
            db.commit()
            db.refresh(merchant)
        return merchant
    
    def increment_order_count(self, db: Session, *, merchant_id: int) -> Optional[Merchant]:
        """增加订单计数"""
        merchant = self.get(db, id=merchant_id)
        if merchant:
            merchant.total_orders += 1
            db.add(merchant)
            db.commit()
            db.refresh(merchant)
        return merchant


# 创建CRUD实例
crud_merchant = CRUDMerchant(Merchant) 
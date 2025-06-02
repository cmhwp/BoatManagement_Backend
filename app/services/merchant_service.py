from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud.merchant import crud_merchant
from app.crud.user import crud_user
from app.schemas.merchant import MerchantCreate, MerchantUpdate, MerchantResponse, MerchantVerification
from app.models.merchant import MerchantStatus, VerificationLevel
from app.models.user import UserRole
from app.utils.logger import logger
from app.utils.validators import validate_business_license


class MerchantService:
    """商家服务类"""
    
    @staticmethod
    def register_merchant(db: Session, user_id: int, merchant_create: MerchantCreate) -> MerchantResponse:
        """商家入驻申请"""
        # 检查用户是否存在且有商家权限
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if user.role != UserRole.MERCHANT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家角色用户才能申请入驻"
            )
        
        # 检查用户是否已经入驻
        existing_merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if existing_merchant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户已经入驻过商家"
            )
        
        # 检查营业执照是否已被使用
        existing_license = crud_merchant.get_by_business_license(
            db, business_license=merchant_create.business_license
        )
        if existing_license:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该营业执照已被使用"
            )
        
        # 验证营业执照格式
        if not validate_business_license(merchant_create.business_license):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="营业执照格式不正确"
            )
        
        # 创建商家记录
        merchant_data = merchant_create.model_dump()
        merchant_data["user_id"] = user_id
        merchant_data["status"] = MerchantStatus.PENDING
        merchant_data["verification_level"] = VerificationLevel.UNVERIFIED
        
        merchant = crud_merchant.create(db, obj_in=merchant_data)
        
        logger.info(f"商家入驻申请提交: {merchant.business_name}, 用户ID: {user_id}")
        
        return MerchantResponse.model_validate(merchant)
    
    @staticmethod
    def get_merchant_profile(db: Session, user_id: int) -> MerchantResponse:
        """获取商家资料"""
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商家信息不存在"
            )
        
        return MerchantResponse.model_validate(merchant)
    
    @staticmethod
    def update_merchant_profile(
        db: Session, 
        user_id: int, 
        merchant_update: MerchantUpdate
    ) -> MerchantResponse:
        """更新商家资料"""
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商家信息不存在"
            )
        
        # 检查商家状态是否允许修改
        if merchant.status == MerchantStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家已被暂停，无法修改信息"
            )
        
        updated_merchant = crud_merchant.update(db, db_obj=merchant, obj_in=merchant_update)
        
        logger.info(f"商家资料更新: {merchant.business_name}")
        
        return MerchantResponse.model_validate(updated_merchant)
    
    @staticmethod
    def get_merchant_by_id(db: Session, merchant_id: int) -> MerchantResponse:
        """根据ID获取商家信息"""
        merchant = crud_merchant.get(db, id=merchant_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商家不存在"
            )
        
        return MerchantResponse.model_validate(merchant)
    
    @staticmethod
    def get_merchants_list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[MerchantStatus] = None,
        verification_level: Optional[VerificationLevel] = None,
        keyword: Optional[str] = None
    ) -> dict:
        """获取商家列表"""
        filters = {}
        if status:
            filters["status"] = status
        if verification_level:
            filters["verification_level"] = verification_level
        
        if keyword:
            merchants = crud_merchant.search_merchants(
                db, keyword=keyword, skip=skip, limit=limit
            )
            total = len(merchants)
        else:
            merchants = crud_merchant.get_multi(
                db, skip=skip, limit=limit, filters=filters, order_by="-created_at"
            )
            total = crud_merchant.count(db, filters=filters)
        
        return {
            "merchants": [MerchantResponse.model_validate(m).model_dump() for m in merchants],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def verify_merchant(
        db: Session, 
        merchant_id: int, 
        verification: MerchantVerification,
        operator_id: int
    ) -> dict:
        """商家认证（管理员功能）"""
        merchant = crud_merchant.get(db, id=merchant_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商家不存在"
            )
        
        # 更新认证信息
        update_data = {
            "verification_level": verification.verification_level,
            "verification_notes": verification.verification_notes,
            "verified_by": operator_id
        }
        
        # 如果认证通过，激活商家
        if verification.verification_level in [VerificationLevel.BASIC, VerificationLevel.PREMIUM]:
            update_data["status"] = MerchantStatus.ACTIVE
            from datetime import datetime
            update_data["verified_at"] = datetime.utcnow()
        
        crud_merchant.update(db, db_obj=merchant, obj_in=update_data)
        
        logger.info(f"商家认证完成: {merchant.business_name}, 认证级别: {verification.verification_level}")
        
        return {
            "message": "商家认证完成",
            "merchant_id": merchant_id,
            "verification_level": verification.verification_level
        }
    
    @staticmethod
    def suspend_merchant(db: Session, merchant_id: int, operator_id: int, reason: str) -> dict:
        """暂停商家（管理员功能）"""
        merchant = crud_merchant.get(db, id=merchant_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商家不存在"
            )
        
        crud_merchant.update(db, db_obj=merchant, obj_in={
            "status": MerchantStatus.SUSPENDED,
            "suspension_reason": reason
        })
        
        logger.info(f"商家已暂停: {merchant.business_name}, 操作者ID: {operator_id}")
        
        return {"message": f"商家 {merchant.business_name} 已被暂停"}
    
    @staticmethod
    def get_nearby_merchants(
        db: Session,
        latitude: float,
        longitude: float,
        radius: float = 10.0,
        skip: int = 0,
        limit: int = 100
    ) -> dict:
        """获取附近商家"""
        merchants = crud_merchant.get_merchants_by_location(
            db,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            skip=skip,
            limit=limit
        )
        
        return {
            "merchants": [MerchantResponse.model_validate(m).model_dump() for m in merchants],
            "total": len(merchants),
            "radius": radius
        } 
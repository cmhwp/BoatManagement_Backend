from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.identity_verification import IdentityVerification
from app.models.enums import VerificationStatus
from app.schemas.identity_verification import (
    IdentityVerificationCreate,
    IdentityVerificationUpdate,
    IdentityVerificationReview
)


class CRUDIdentityVerification:
    """实名认证CRUD操作类"""

    def create(self, db: Session, *, obj_in: IdentityVerificationCreate, user_id: int) -> IdentityVerification:
        """创建实名认证申请"""
        # 检查用户是否已有待审核或通过的实名认证
        existing = self.get_by_user_id(db, user_id=user_id)
        if existing and existing.status in [VerificationStatus.PENDING, VerificationStatus.APPROVED]:
            raise ValueError("用户已存在待审核或已通过的实名认证")
        
        db_obj = IdentityVerification(
            user_id=user_id,
            real_name=obj_in.real_name,
            identity_type=obj_in.identity_type,
            identity_number=obj_in.identity_number,
            front_image=obj_in.front_image,
            back_image=obj_in.back_image,
            status=VerificationStatus.PENDING
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[IdentityVerification]:
        """根据ID获取实名认证信息"""
        return db.query(IdentityVerification).filter(IdentityVerification.id == id).first()

    def get_by_user_id(self, db: Session, user_id: int) -> Optional[IdentityVerification]:
        """根据用户ID获取实名认证信息"""
        return db.query(IdentityVerification).filter(
            IdentityVerification.user_id == user_id
        ).first()

    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[VerificationStatus] = None
    ) -> List[IdentityVerification]:
        """获取实名认证列表"""
        query = db.query(IdentityVerification)
        
        if status:
            query = query.filter(IdentityVerification.status == status)
        
        return query.offset(skip).limit(limit).all()

    def get_pending_count(self, db: Session) -> int:
        """获取待审核的实名认证数量"""
        return db.query(IdentityVerification).filter(
            IdentityVerification.status == VerificationStatus.PENDING
        ).count()

    def update(
        self, 
        db: Session, 
        *, 
        db_obj: IdentityVerification, 
        obj_in: IdentityVerificationUpdate
    ) -> IdentityVerification:
        """更新实名认证信息（仅允许待审核状态下更新）"""
        if db_obj.status != VerificationStatus.PENDING:
            raise ValueError("只能更新待审核状态的实名认证")
        
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def review(
        self, 
        db: Session, 
        *, 
        db_obj: IdentityVerification, 
        obj_in: IdentityVerificationReview,
        reviewer_id: int
    ) -> IdentityVerification:
        """审核实名认证"""
        if db_obj.status != VerificationStatus.PENDING:
            raise ValueError("只能审核待审核状态的实名认证")
        
        # 更新审核信息
        db_obj.status = obj_in.status
        db_obj.reviewer_id = reviewer_id
        db_obj.reviewed_at = datetime.utcnow()
        
        if obj_in.status == VerificationStatus.APPROVED:
            db_obj.verified_at = datetime.utcnow()
            # 设置认证有效期（默认3年）
            if obj_in.expires_at:
                db_obj.expires_at = obj_in.expires_at
            else:
                db_obj.expires_at = datetime.utcnow() + timedelta(days=365*3)
            
            # 更新用户的实名认证状态
            from app.models.user import User
            user = db.query(User).filter(User.id == db_obj.user_id).first()
            if user:
                user.is_verified = True
        
        elif obj_in.status == VerificationStatus.REJECTED:
            db_obj.reject_reason = obj_in.reject_reason
            
            # 如果用户之前已实名认证，需要取消认证状态
            from app.models.user import User
            user = db.query(User).filter(User.id == db_obj.user_id).first()
            if user:
                user.is_verified = False
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def check_expired(self, db: Session) -> List[IdentityVerification]:
        """检查过期的实名认证"""
        return db.query(IdentityVerification).filter(
            and_(
                IdentityVerification.status == VerificationStatus.APPROVED,
                IdentityVerification.expires_at < datetime.utcnow()
            )
        ).all()

    def mark_expired(self, db: Session, verification_ids: List[int]) -> int:
        """标记实名认证为过期"""
        count = db.query(IdentityVerification).filter(
            IdentityVerification.id.in_(verification_ids)
        ).update(
            {
                IdentityVerification.status: VerificationStatus.EXPIRED,
                IdentityVerification.updated_at: datetime.utcnow()
            },
            synchronize_session=False
        )
        
        # 同时更新用户的实名认证状态
        from app.models.user import User
        user_ids = db.query(IdentityVerification.user_id).filter(
            IdentityVerification.id.in_(verification_ids)
        ).all()
        
        if user_ids:
            db.query(User).filter(
                User.id.in_([uid[0] for uid in user_ids])
            ).update(
                {User.is_verified: False},
                synchronize_session=False
            )
        
        db.commit()
        return count

    def get_statistics(self, db: Session) -> dict:
        """获取实名认证统计信息"""
        total = db.query(IdentityVerification).count()
        pending = db.query(IdentityVerification).filter(
            IdentityVerification.status == VerificationStatus.PENDING
        ).count()
        approved = db.query(IdentityVerification).filter(
            IdentityVerification.status == VerificationStatus.APPROVED
        ).count()
        rejected = db.query(IdentityVerification).filter(
            IdentityVerification.status == VerificationStatus.REJECTED
        ).count()
        expired = db.query(IdentityVerification).filter(
            IdentityVerification.status == VerificationStatus.EXPIRED
        ).count()
        
        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "expired": expired
        }


# 创建全局实例
identity_verification = CRUDIdentityVerification() 
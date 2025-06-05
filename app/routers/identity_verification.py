from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.deps import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.enums import VerificationStatus
from app.schemas.identity_verification import (
    IdentityVerificationCreate,
    IdentityVerificationUpdate,
    IdentityVerificationReview,
    IdentityVerificationResponse,
    IdentityVerificationSummary
)
from app.schemas.common import PaginatedResponse, ApiResponse
from app.crud.identity_verification import identity_verification

router = APIRouter(prefix="/api/v1/identity-verification", tags=["identity"])


@router.post("/", response_model=ApiResponse[IdentityVerificationResponse])
def create_identity_verification(
    verification_in: IdentityVerificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交实名认证申请
    
    用户提交实名认证信息，等待管理员审核
    """
    try:
        verification = identity_verification.create(
            db=db, 
            obj_in=verification_in, 
            user_id=current_user.id
        )
        return ApiResponse(
            success=True,
            message="实名认证申请提交成功，等待审核",
            data=verification
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=ApiResponse[Optional[IdentityVerificationResponse]])
def get_my_identity_verification(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取我的实名认证信息
    """
    verification = identity_verification.get_by_user_id(db=db, user_id=current_user.id)
    return ApiResponse(
        success=True,
        message="获取成功",
        data=verification
    )


@router.put("/me", response_model=ApiResponse[IdentityVerificationResponse])
def update_my_identity_verification(
    verification_in: IdentityVerificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新我的实名认证信息
    
    只能更新待审核状态的实名认证
    """
    verification = identity_verification.get_by_user_id(db=db, user_id=current_user.id)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="实名认证信息不存在"
        )
    
    try:
        updated_verification = identity_verification.update(
            db=db,
            db_obj=verification,
            obj_in=verification_in
        )
        return ApiResponse(
            success=True,
            message="实名认证信息更新成功",
            data=updated_verification
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=PaginatedResponse[IdentityVerificationSummary])
def get_identity_verifications(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数"),
    status: Optional[VerificationStatus] = Query(None, description="认证状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取实名认证列表（管理员）
    
    管理员可以查看所有用户的实名认证申请
    """
    verifications = identity_verification.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        status=status
    )
    
    # 获取总数
    from app.models.identity_verification import IdentityVerification
    query = db.query(IdentityVerification)
    if status:
        query = query.filter(IdentityVerification.status == status)
    total = query.count()
    
    return PaginatedResponse(
        success=True,
        message="获取成功",
        data=verifications,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{verification_id}", response_model=ApiResponse[IdentityVerificationResponse])
def get_identity_verification(
    verification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取实名认证详情（管理员）
    """
    verification = identity_verification.get(db=db, id=verification_id)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="实名认证信息不存在"
        )
    
    return ApiResponse(
        success=True,
        message="获取成功",
        data=verification
    )


@router.post("/{verification_id}/review", response_model=ApiResponse[IdentityVerificationResponse])
def review_identity_verification(
    verification_id: int,
    review_in: IdentityVerificationReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    审核实名认证（管理员）
    
    管理员可以通过或拒绝用户的实名认证申请
    """
    verification = identity_verification.get(db=db, id=verification_id)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="实名认证信息不存在"
        )
    
    try:
        reviewed_verification = identity_verification.review(
            db=db,
            db_obj=verification,
            obj_in=review_in,
            reviewer_id=current_user.id
        )
        
        action_msg = {
            VerificationStatus.APPROVED: "通过",
            VerificationStatus.REJECTED: "拒绝"
        }.get(review_in.status, "审核")
        
        return ApiResponse(
            success=True,
            message=f"实名认证{action_msg}成功",
            data=reviewed_verification
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/statistics/overview", response_model=ApiResponse[dict])
def get_verification_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取实名认证统计信息（管理员）
    """
    stats = identity_verification.get_statistics(db=db)
    return ApiResponse(
        success=True,
        message="获取成功",
        data=stats
    )


@router.post("/check-expired", response_model=ApiResponse[dict])
def check_expired_verifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    检查并处理过期的实名认证（管理员）
    """
    expired_verifications = identity_verification.check_expired(db=db)
    
    if expired_verifications:
        expired_ids = [v.id for v in expired_verifications]
        count = identity_verification.mark_expired(db=db, verification_ids=expired_ids)
        
        return ApiResponse(
            success=True,
            message=f"已处理 {count} 个过期的实名认证",
            data={"expired_count": count}
        )
    else:
        return ApiResponse(
            success=True,
            message="没有过期的实名认证",
            data={"expired_count": 0}
        ) 
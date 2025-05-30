from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.merchants import MerchantResponse, MerchantCreate
from app.crud import merchants as crud_merchants
from app.utils.auth import get_current_active_user, check_user_role
from app.models.users import User, UserRole

router = APIRouter(
    prefix="/merchants",
    tags=["商家管理"]
)

@router.post("/", response_model=MerchantResponse, summary="创建商家")
def create_merchant(
    merchant: MerchantCreate,
    current_user: User = Depends(check_user_role([UserRole.merchant])),
    db: Session = Depends(get_db)
):
    return crud_merchants.create_merchant(db, current_user.user_id, merchant) 
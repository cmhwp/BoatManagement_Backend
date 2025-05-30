from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.users import UserResponse, UserUpdate, RoleApplicationCreate, RoleApplicationResponse
from app.crud import users as crud_users
from app.utils.auth import get_current_active_user
from app.models.users import User

router = APIRouter(
    prefix="/users",
    tags=["用户管理"]
)

@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=UserResponse, summary="更新用户信息")
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud_users.update_user(db, current_user.user_id, user_update)

@router.post("/role-application", response_model=RoleApplicationResponse, summary="申请角色")
def apply_role(
    application: RoleApplicationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud_users.create_role_application(db, current_user.user_id, application) 
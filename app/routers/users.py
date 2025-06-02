from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.user import UserUpdate, UserResponse, RoleApplicationCreate
from app.services.user_service import UserService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.dependencies import get_current_user, require_admin
from app.models.user import UserRole

router = APIRouter()


@router.get("/profile", response_model=UserResponse, summary="获取个人资料")
async def get_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的个人资料"""
    try:
        result = UserService.get_user_profile(db, current_user.id)
        return success_response(
            message="获取个人资料成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.put("/profile", summary="更新个人资料")
async def update_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户的个人资料"""
    try:
        result = UserService.update_user_profile(db, current_user.id, user_update)
        return success_response(
            message="资料更新成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/upload-avatar", summary="上传头像")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传用户头像"""
    try:
        result = await UserService.upload_user_avatar(db, current_user.id, file)
        return success_response(
            message="头像上传成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/apply-role", summary="申请角色")
async def apply_role(
    application: RoleApplicationCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """申请新角色"""
    try:
        result = UserService.apply_role(db, current_user.id, application)
        return success_response(
            message="角色申请已提交",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/applications", summary="获取角色申请记录")
async def get_applications(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的角色申请记录"""
    try:
        result = UserService.get_user_applications(db, current_user.id)
        return success_response(
            message="获取申请记录成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/{user_id}", summary="获取指定用户信息")
async def get_user(
    user_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定用户的公开信息（需要登录）"""
    try:
        result = UserService.get_user_profile(db, user_id)
        # 过滤敏感信息
        public_data = result.model_dump()
        public_data.pop("email", None)
        public_data.pop("phone", None)
        
        return success_response(
            message="获取用户信息成功",
            data=public_data
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


# 管理员功能
@router.get("", summary="获取用户列表")
async def get_users_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    role: Optional[UserRole] = Query(None, description="用户角色筛选"),
    status: Optional[str] = Query(None, description="用户状态筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取用户列表（管理员功能）"""
    try:
        skip = (page - 1) * size
        result = UserService.get_users_list(
            db=db,
            skip=skip,
            limit=size,
            role=role,
            status=status,
            keyword=keyword
        )
        
        return paginated_response(
            data=result["users"],
            total=result["total"],
            page=page,
            size=size,
            message="获取用户列表成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/{user_id}/deactivate", summary="禁用用户")
async def deactivate_user(
    user_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """禁用指定用户（管理员功能）"""
    try:
        result = UserService.deactivate_user(db, user_id, current_user.id)
        return success_response(
            message="用户已禁用",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/{user_id}/activate", summary="激活用户")
async def activate_user(
    user_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """激活指定用户（管理员功能）"""
    try:
        result = UserService.activate_user(db, user_id, current_user.id)
        return success_response(
            message="用户已激活",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code) 
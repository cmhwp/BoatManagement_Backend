from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, TokenResponse, PasswordChange
from app.services.auth_service import AuthService
from app.utils.response import success_response, error_response
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post("/register", summary="用户注册")
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册接口"""
    try:
        result = AuthService.register(db, user_create)
        return success_response(
            message="注册成功",
            data=result
        )
    except HTTPException as e:
        return error_response(
            message=e.detail,
            status_code=e.status_code
        )


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """用户登录接口"""
    try:
        result = AuthService.login(db, user_login)
        return success_response(
            message="登录成功",
            data=result.dict()
        )
    except HTTPException as e:
        return error_response(
            message=e.detail,
            status_code=e.status_code
        )


@router.post("/refresh", summary="刷新令牌")
async def refresh_token(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    try:
        result = AuthService.refresh_token(db, current_user.id)
        return success_response(
            message="令牌刷新成功",
            data=result
        )
    except HTTPException as e:
        return error_response(
            message=e.detail,
            status_code=e.status_code
        )


@router.post("/change-password", summary="修改密码")
async def change_password(
    password_change: PasswordChange,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码接口"""
    try:
        result = AuthService.change_password(
            db,
            current_user.id,
            password_change.old_password,
            password_change.new_password
        )
        return success_response(
            message="密码修改成功",
            data=result
        )
    except HTTPException as e:
        return error_response(
            message=e.detail,
            status_code=e.status_code
        )


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """获取当前登录用户信息"""
    from app.schemas.user import UserResponse
    return success_response(
        message="获取用户信息成功",
        data=UserResponse.from_orm(current_user).dict()
    )


@router.post("/logout", summary="用户退出")
async def logout():
    """用户退出登录（客户端需要删除本地token）"""
    return success_response(
        message="退出登录成功",
        data={"message": "请删除本地存储的访问令牌"}
    ) 
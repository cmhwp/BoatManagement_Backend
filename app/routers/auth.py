from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from app.config.database import get_db
from app.config.settings import settings
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.crud.user import create_user, authenticate_user, update_last_login
from app.utils.security import create_access_token
from app.utils.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    
    - **username**: 用户名（3位以上）
    - **email**: 邮箱地址
    - **password**: 密码（6位以上）
    - **phone**: 手机号（可选）
    - **real_name**: 真实姓名（可选）
    - **role**: 用户角色，默认为普通用户
    """
    try:
        db_user = create_user(db=db, user=user)
        return UserResponse.from_orm(db_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.post("/login", response_model=Token, summary="用户登录")
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    
    - **username**: 用户名、邮箱或手机号
    - **password**: 密码
    
    返回访问令牌和用户信息
    """
    user = authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户状态
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号已被停用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires
    )
    
    # 更新最后登录时间
    update_last_login(db, user.id)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前登录用户的详细信息"""
    return UserResponse.from_orm(current_user)


@router.post("/logout", summary="用户登出")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    用户登出接口
    
    注意：JWT令牌是无状态的，无法在服务端主动失效。
    客户端应该删除本地存储的令牌。
    """
    return {"message": "登出成功"} 
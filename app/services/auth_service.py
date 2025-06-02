from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud.user import crud_user
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.utils.jwt_handler import create_access_token
from app.utils.password import verify_password
from app.utils.logger import logger


class AuthService:
    """认证服务类"""
    
    @staticmethod
    def register(db: Session, user_create: UserCreate) -> dict:
        """用户注册"""
        # 检查用户名是否已存在
        existing_user = crud_user.get_by_username(db, username=user_create.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        existing_email = crud_user.get_by_email(db, email=user_create.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 检查手机号是否已存在（如果提供）
        if user_create.phone:
            existing_phone = crud_user.get_by_phone(db, phone=user_create.phone)
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="手机号已被注册"
                )
        
        # 创建用户
        try:
            user = crud_user.create(db, obj_in=user_create)
            logger.info(f"用户注册成功: {user.username}")
            return {
                "message": "注册成功",
                "user_id": user.id,
                "username": user.username
            }
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="注册失败，请稍后重试"
            )
    
    @staticmethod
    def login(db: Session, user_login: UserLogin) -> TokenResponse:
        """用户登录"""
        # 验证用户凭据
        user = crud_user.authenticate(
            db, 
            username=user_login.username, 
            password=user_login.password
        )
        
        if not user:
            logger.warning(f"登录失败 - 无效凭据: {user_login.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 检查用户状态
        if not crud_user.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用"
            )
        
        # 生成访问令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # 更新最后登录时间
        crud_user.update_last_login(db, user=user)
        
        logger.info(f"用户登录成功: {user.username}")
        
        # 返回token响应
        from app.schemas.user import UserResponse
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,  # 1小时
            user=UserResponse.from_orm(user)
        )
    
    @staticmethod
    def refresh_token(db: Session, user_id: int) -> dict:
        """刷新访问令牌"""
        user = crud_user.get(db, id=user_id)
        if not user or not crud_user.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用"
            )
        
        # 生成新的访问令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
    
    @staticmethod
    def get_current_user(db: Session, user_id: int):
        """获取当前用户"""
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if not crud_user.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用"
            )
        
        return user
    
    @staticmethod
    def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> dict:
        """修改密码"""
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证旧密码
        if not verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原密码错误"
            )
        
        # 更新密码
        crud_user.update_password(db, user=user, new_password=new_password)
        
        logger.info(f"用户修改密码成功: {user.username}")
        
        return {"message": "密码修改成功"}
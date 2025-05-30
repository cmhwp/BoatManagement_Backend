from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import Token, UserLogin, UserRegister
from app.schemas.users import UserResponse
from app.crud import users as crud_users
from app.utils.security import verify_password
from app.utils.auth import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["认证"]
)


@router.post("/register", response_model=UserResponse, summary="用户注册")
def register(user: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    if crud_users.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    
    # 检查手机号是否已存在
    if crud_users.get_user_by_phone(db, user.phone):
        raise HTTPException(
            status_code=400,
            detail="手机号已被注册"
        )
    
    # 检查邮箱是否已存在
    if user.email and crud_users.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="邮箱已被注册"
        )
    
    # 创建用户
    from app.schemas.users import UserCreate
    user_create = UserCreate(**user.model_dump())
    db_user = crud_users.create_user(db, user_create)
    return db_user


@router.post("/login", response_model=Token, summary="用户登录")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 获取用户
    user = crud_users.get_user_by_username(db, user_credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新最后登录时间
    crud_users.update_last_login(db, user.user_id)
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": str(user.user_id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token, summary="OAuth2兼容登录")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2兼容的登录接口"""
    user = crud_users.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新最后登录时间
    crud_users.update_last_login(db, user.user_id)
    
    access_token = create_access_token(data={"sub": str(user.user_id)})
    return {"access_token": access_token, "token_type": "bearer"} 
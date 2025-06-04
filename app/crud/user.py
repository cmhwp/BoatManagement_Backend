from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from datetime import datetime
from app.models.user import User
from app.models.enums import UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.common import PaginationParams
from app.utils.security import get_password_hash, verify_password


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    """根据手机号获取用户"""
    return db.query(User).filter(User.phone == phone).first()


def get_user_by_login_credential(db: Session, credential: str) -> Optional[User]:
    """根据登录凭证（用户名、邮箱或手机号）获取用户"""
    return db.query(User).filter(
        or_(
            User.username == credential,
            User.email == credential,
            User.phone == credential
        )
    ).first()


def get_users(
    db: Session,
    pagination: PaginationParams,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    is_verified: Optional[bool] = None,
    search: Optional[str] = None
) -> tuple[List[User], int]:
    """获取用户列表"""
    query = db.query(User)
    
    # 应用过滤条件
    if role:
        query = query.filter(User.role == role)
    
    if status:
        query = query.filter(User.status == status)
    
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    
    if search:
        query = query.filter(
            or_(
                User.username.contains(search),
                User.email.contains(search),
                User.real_name.contains(search),
                User.phone.contains(search)
            )
        )
    
    # 获取总数
    total = query.count()
    
    # 应用分页
    users = query.offset(pagination.get_offset()).limit(pagination.get_limit()).all()
    
    return users, total


def create_user(db: Session, user: UserCreate) -> User:
    """创建用户"""
    # 检查用户名是否已存在
    if get_user_by_username(db, user.username):
        raise ValueError("用户名已存在")
    
    # 检查邮箱是否已存在
    if get_user_by_email(db, user.email):
        raise ValueError("邮箱已存在")
    
    # 检查手机号是否已存在（如果提供了手机号）
    if user.phone and get_user_by_phone(db, user.phone):
        raise ValueError("手机号已存在")
    
    # 创建用户实例
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_password,
        real_name=user.real_name,
        gender=user.gender,
        address=user.address,
        role=user.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, credential: str, password: str) -> Optional[User]:
    """验证用户身份"""
    user = get_user_by_login_credential(db, credential)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def update_last_login(db: Session, user_id: int) -> None:
    """更新用户最后登录时间"""
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.last_login_at = datetime.now()
        db.commit()


def delete_user(db: Session, user_id: int) -> bool:
    """删除用户"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True 
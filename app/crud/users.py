from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from app.models.users import User, UserRole
from app.models.role_applications import RoleApplication, TargetRole, ApplicationStatus
from app.schemas.users import UserCreate, UserUpdate, RoleApplicationCreate
from app.utils.security import get_password_hash
from datetime import datetime


def get_user(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.user_id == user_id, User.is_delete == False).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username, User.is_delete == False).first()


def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    """根据手机号获取用户"""
    return db.query(User).filter(User.phone == phone, User.is_delete == False).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email, User.is_delete == False).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """获取用户列表"""
    return db.query(User).filter(User.is_delete == False).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """创建用户"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        password_hash=hashed_password,
        phone=user.phone,
        email=user.email,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db_user.update_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """软删除用户"""
    db_user = get_user(db, user_id)
    if db_user:
        db_user.is_delete = True
        db_user.update_at = datetime.utcnow()
        db.commit()
        return True
    return False


def update_last_login(db: Session, user_id: int):
    """更新最后登录时间"""
    db_user = get_user(db, user_id)
    if db_user:
        db_user.last_login = datetime.utcnow()
        db.commit()


def create_role_application(db: Session, user_id: int, application: RoleApplicationCreate) -> RoleApplication:
    """创建角色申请"""
    db_application = RoleApplication(
        user_id=user_id,
        target_role=TargetRole(application.target_role),
        application_data=application.application_data
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def get_role_applications(db: Session, skip: int = 0, limit: int = 100) -> List[RoleApplication]:
    """获取角色申请列表"""
    return db.query(RoleApplication).offset(skip).limit(limit).all()


def get_user_role_applications(db: Session, user_id: int) -> List[RoleApplication]:
    """获取用户的角色申请"""
    return db.query(RoleApplication).filter(RoleApplication.user_id == user_id).all()


def approve_role_application(db: Session, application_id: int, review_notes: str = None) -> Optional[RoleApplication]:
    """批准角色申请"""
    db_application = db.query(RoleApplication).filter(RoleApplication.application_id == application_id).first()
    if db_application:
        db_application.status = ApplicationStatus.approved
        db_application.reviewed_time = datetime.utcnow()
        db_application.review_notes = review_notes
        
        # 更新用户角色
        user = get_user(db, db_application.user_id)
        if user:
            user.role = UserRole(db_application.target_role.value)
            user.update_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_application)
    return db_application


def reject_role_application(db: Session, application_id: int, review_notes: str = None) -> Optional[RoleApplication]:
    """拒绝角色申请"""
    db_application = db.query(RoleApplication).filter(RoleApplication.application_id == application_id).first()
    if db_application:
        db_application.status = ApplicationStatus.rejected
        db_application.reviewed_time = datetime.utcnow()
        db_application.review_notes = review_notes
        db.commit()
        db.refresh(db_application)
    return db_application 
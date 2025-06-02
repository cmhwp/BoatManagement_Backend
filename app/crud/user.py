from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User, RoleApplication
from app.schemas.user import UserCreate, UserUpdate
from app.utils.password import hash_password, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """用户CRUD操作类"""
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()
    
    def get_by_phone(self, db: Session, *, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        return db.query(User).filter(User.phone == phone).first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """创建用户（加密密码）"""
        create_data = obj_in.dict()
        create_data.pop("password")
        db_obj = User(
            **create_data,
            password_hash=hash_password(obj_in.password)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """验证用户登录"""
        user = self.get_by_username(db, username=username)
        if not user:
            # 尝试邮箱登录
            user = self.get_by_email(db, email=username)
        if not user:
            # 尝试手机号登录
            user = self.get_by_phone(db, phone=username)
        
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        """检查用户是否激活"""
        return user.status.value == "active"
    
    def is_verified(self, user: User) -> bool:
        """检查用户是否已验证"""
        return user.is_verified
    
    def update_password(self, db: Session, *, user: User, new_password: str) -> User:
        """更新用户密码"""
        user.password_hash = hash_password(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def update_last_login(self, db: Session, *, user: User) -> User:
        """更新最后登录时间"""
        from datetime import datetime
        user.last_login = datetime.now()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


class CRUDRoleApplication(CRUDBase[RoleApplication, dict, dict]):
    """角色申请CRUD操作类"""
    
    def get_by_user(self, db: Session, *, user_id: int, status: Optional[str] = None):
        """获取用户的角色申请记录"""
        query = db.query(RoleApplication).filter(RoleApplication.user_id == user_id)
        if status:
            query = query.filter(RoleApplication.status == status)
        return query.all()
    
    def get_pending_applications(self, db: Session, *, skip: int = 0, limit: int = 100):
        """获取待审核的申请"""
        return db.query(RoleApplication).filter(
            RoleApplication.status == "pending"
        ).offset(skip).limit(limit).all()


# 创建CRUD实例
crud_user = CRUDUser(User)
crud_role_application = CRUDRoleApplication(RoleApplication) 
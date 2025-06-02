from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from app.crud.user import crud_user, crud_role_application
from app.schemas.user import UserUpdate, UserResponse, RoleApplicationCreate
from app.models.user import UserRole, ApplicationStatus
from app.utils.logger import logger
from app.utils.file_handler import upload_avatar
from app.utils.dependencies import get_current_user


class UserService:
    """用户服务类"""
    
    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> UserResponse:
        """获取用户资料"""
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return UserResponse.model_validate(user)
    
    @staticmethod
    def update_user_profile(db: Session, user_id: int, user_update: UserUpdate) -> UserResponse:
        """更新用户资料"""
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查手机号是否已被其他用户使用
        if user_update.phone and user_update.phone != user.phone:
            existing_phone = crud_user.get_by_phone(db, phone=user_update.phone)
            if existing_phone and existing_phone.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="手机号已被其他用户使用"
                )
        
        updated_user = crud_user.update(db, db_obj=user, obj_in=user_update)
        logger.info(f"用户资料更新成功: {user.username}")
        
        return UserResponse.model_validate(updated_user)
    
    @staticmethod
    async def upload_user_avatar(db: Session, user_id: int, file: UploadFile) -> dict:
        """上传用户头像"""
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        try:
            # 上传头像文件
            file_info = await upload_avatar(file)
            
            # 更新用户头像URL
            crud_user.update(db, db_obj=user, obj_in={"avatar": file_info["file_url"]})
            
            logger.info(f"用户头像上传成功: {user.username}")
            
            return {
                "message": "头像上传成功",
                "avatar_url": file_info["file_url"],
                "thumbnail_url": file_info.get("thumbnail_url")
            }
        except Exception as e:
            logger.error(f"头像上传失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="头像上传失败"
            )
    
    @staticmethod
    def apply_role(db: Session, user_id: int, application: RoleApplicationCreate) -> dict:
        """申请角色"""
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查是否已经是目标角色
        if user.role == application.target_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已经是该角色"
            )
        
        # 检查是否有待审核的申请
        pending_applications = crud_role_application.get_by_user(
            db, user_id=user_id, status="pending"
        )
        if pending_applications:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您有待审核的角色申请，请等待审核结果"
            )
        
        # 创建角色申请
        from app.models.user import RoleApplication
        application_data = {
            "user_id": user_id,
            "target_role": application.target_role,
            "application_reason": application.application_reason,
            "supporting_documents": str(application.supporting_documents) if application.supporting_documents else None,
            "status": ApplicationStatus.PENDING
        }
        
        db_application = RoleApplication(**application_data)
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        
        logger.info(f"用户角色申请提交: {user.username} -> {application.target_role}")
        
        return {
            "message": "角色申请已提交，请等待审核",
            "application_id": db_application.id,
            "target_role": application.target_role
        }
    
    @staticmethod
    def get_user_applications(db: Session, user_id: int) -> List[dict]:
        """获取用户的角色申请记录"""
        applications = crud_role_application.get_by_user(db, user_id=user_id)
        
        return [
            {
                "id": app.id,
                "target_role": app.target_role,
                "status": app.status,
                "application_reason": app.application_reason,
                "review_comment": app.review_comment,
                "created_at": app.created_at,
                "reviewed_at": app.reviewed_at
            }
            for app in applications
        ]
    
    @staticmethod
    def get_users_list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> dict:
        """获取用户列表（管理员功能）"""
        filters = {}
        if role:
            filters["role"] = role
        if status:
            filters["status"] = status
        
        if keyword:
            users = crud_user.search(
                db,
                keyword=keyword,
                search_fields=["username", "real_name", "email"],
                skip=skip,
                limit=limit
            )
            total = len(users)  # 搜索情况下的简单计数
        else:
            users = crud_user.get_multi(
                db,
                skip=skip,
                limit=limit,
                filters=filters,
                order_by="-created_at"
            )
            total = crud_user.count(db, filters=filters)
        
        return {
            "users": [UserResponse.model_validate(user).model_dump() for user in users],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int, operator_id: int) -> dict:
        """禁用用户（管理员功能）"""
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if user.id == operator_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能禁用自己的账户"
            )
        
        from app.models.user import UserStatus
        crud_user.update(db, db_obj=user, obj_in={"status": UserStatus.INACTIVE})
        
        logger.info(f"用户已被禁用: {user.username}, 操作者ID: {operator_id}")
        
        return {"message": f"用户 {user.username} 已被禁用"}
    
    @staticmethod
    def activate_user(db: Session, user_id: int, operator_id: int) -> dict:
        """激活用户（管理员功能）"""
        user = crud_user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        from app.models.user import UserStatus
        crud_user.update(db, db_obj=user, obj_in={"status": UserStatus.ACTIVE})
        
        logger.info(f"用户已被激活: {user.username}, 操作者ID: {operator_id}")
        
        return {"message": f"用户 {user.username} 已被激活"} 
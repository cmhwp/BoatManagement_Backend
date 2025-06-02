from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
import json
from app.crud.boat import crud_boat
from app.crud.merchant import crud_merchant
from app.schemas.boat import (
    BoatCreate, BoatUpdate, BoatResponse, BoatListResponse, 
    BoatStatusUpdate, BoatMaintenanceUpdate
)
from app.models.boat import BoatStatus, BoatType
from app.models.merchant import MerchantStatus
from app.utils.logger import logger
from app.utils.file_handler import upload_image


class BoatService:
    """船艇服务类"""
    
    @staticmethod
    def create_boat(db: Session, user_id: int, boat_create: BoatCreate) -> BoatResponse:
        """创建船艇"""
        # 检查用户是否有商家资质
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能添加船艇"
            )
        
        if merchant.status != MerchantStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家状态异常，无法添加船艇"
            )
        
        # 检查船舶登记号是否已存在
        if boat_create.registration_number:
            existing_boat = crud_boat.get_by_registration_number(
                db, registration_number=boat_create.registration_number
            )
            if existing_boat:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="船舶登记号已存在"
                )
        
        # 准备船艇数据
        boat_data = boat_create.model_dump()
        boat_data["merchant_id"] = merchant.id
        
        # 处理设施和安全设备列表
        if boat_create.amenities:
            boat_data["amenities"] = json.dumps(boat_create.amenities, ensure_ascii=False)
        if boat_create.safety_equipment:
            boat_data["safety_equipment"] = json.dumps(boat_create.safety_equipment, ensure_ascii=False)
        
        boat = crud_boat.create(db, obj_in=boat_data)
        
        logger.info(f"船艇创建成功: {boat.name}, 商家ID: {merchant.id}")
        
        return BoatResponse.model_validate(boat)
    
    @staticmethod
    def get_merchant_boats(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[BoatStatus] = None,
        boat_type: Optional[BoatType] = None
    ) -> dict:
        """获取商家的船艇列表"""
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能查看船艇列表"
            )
        
        boats = crud_boat.get_by_merchant(db, merchant_id=merchant.id, skip=skip, limit=limit)
        
        # 应用筛选条件
        if status or boat_type:
            filtered_boats = []
            for boat in boats:
                if status and boat.status != status:
                    continue
                if boat_type and boat.boat_type != boat_type:
                    continue
                filtered_boats.append(boat)
            boats = filtered_boats
        
        total = crud_boat.get_merchant_boat_count(db, merchant_id=merchant.id)
        
        return {
            "boats": [BoatResponse.model_validate(boat).model_dump() for boat in boats],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_boat_detail(db: Session, boat_id: int, user_id: Optional[int] = None) -> BoatResponse:
        """获取船艇详情"""
        boat = crud_boat.get(db, id=boat_id)
        if not boat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="船艇不存在"
            )
        
        # 如果是商家用户，检查是否有权限查看
        if user_id:
            merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
            if merchant and merchant.id != boat.merchant_id:
                # 非船艇所有者只能查看基本信息
                pass
        
        return BoatResponse.model_validate(boat)
    
    @staticmethod
    def update_boat(db: Session, user_id: int, boat_id: int, boat_update: BoatUpdate) -> BoatResponse:
        """更新船艇信息"""
        boat = crud_boat.get(db, id=boat_id)
        if not boat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="船艇不存在"
            )
        
        # 检查权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant or merchant.id != boat.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改此船艇"
            )
        
        # 处理设施和安全设备列表
        update_data = boat_update.model_dump(exclude_unset=True)
        if boat_update.amenities is not None:
            update_data["amenities"] = json.dumps(boat_update.amenities, ensure_ascii=False)
        if boat_update.safety_equipment is not None:
            update_data["safety_equipment"] = json.dumps(boat_update.safety_equipment, ensure_ascii=False)
        
        updated_boat = crud_boat.update(db, db_obj=boat, obj_in=update_data)
        
        logger.info(f"船艇信息更新: {boat.name}")
        
        return BoatResponse.model_validate(updated_boat)
    
    @staticmethod
    def delete_boat(db: Session, user_id: int, boat_id: int) -> dict:
        """删除船艇"""
        boat = crud_boat.get(db, id=boat_id)
        if not boat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="船艇不存在"
            )
        
        # 检查权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant or merchant.id != boat.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限删除此船艇"
            )
        
        # 检查船艇是否可以删除（没有进行中的服务/订单）
        if boat.status == BoatStatus.OCCUPIED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="船艇使用中，无法删除"
            )
        
        crud_boat.remove(db, id=boat_id)
        
        logger.info(f"船艇删除成功: {boat.name}")
        
        return {"message": f"船艇 {boat.name} 删除成功"}
    
    @staticmethod
    def update_boat_status(db: Session, user_id: int, boat_id: int, status_update: BoatStatusUpdate) -> dict:
        """更新船艇状态"""
        boat = crud_boat.get(db, id=boat_id)
        if not boat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="船艇不存在"
            )
        
        # 检查权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant or merchant.id != boat.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改此船艇状态"
            )
        
        updated_boat = crud_boat.update_status(
            db, boat_id=boat_id, status=status_update.status, notes=status_update.notes
        )
        
        logger.info(f"船艇状态更新: {boat.name} -> {status_update.status}")
        
        return {
            "message": "船艇状态更新成功",
            "boat_id": boat_id,
            "new_status": status_update.status
        }
    
    @staticmethod
    def update_boat_maintenance(db: Session, user_id: int, boat_id: int, maintenance_update: BoatMaintenanceUpdate) -> dict:
        """更新船艇维护信息"""
        boat = crud_boat.get(db, id=boat_id)
        if not boat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="船艇不存在"
            )
        
        # 检查权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant or merchant.id != boat.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改此船艇维护信息"
            )
        
        updated_boat = crud_boat.update(db, db_obj=boat, obj_in=maintenance_update.model_dump(exclude_unset=True))
        
        logger.info(f"船艇维护信息更新: {boat.name}")
        
        return {"message": "船艇维护信息更新成功"}
    
    @staticmethod
    async def upload_boat_images(db: Session, user_id: int, boat_id: int, files: List[UploadFile]) -> dict:
        """上传船艇图片"""
        boat = crud_boat.get(db, id=boat_id)
        if not boat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="船艇不存在"
            )
        
        # 检查权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant or merchant.id != boat.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限上传此船艇图片"
            )
        
        try:
            uploaded_images = []
            for file in files:
                file_info = await upload_image(file, folder="boats")
                uploaded_images.append({
                    "url": file_info["file_url"],
                    "thumbnail": file_info.get("thumbnail_url")
                })
            
            # 更新船艇图片信息
            existing_images = json.loads(boat.images) if boat.images else []
            existing_images.extend(uploaded_images)
            
            crud_boat.update(db, db_obj=boat, obj_in={"images": json.dumps(existing_images, ensure_ascii=False)})
            
            logger.info(f"船艇图片上传成功: {boat.name}, 上传 {len(files)} 张图片")
            
            return {
                "message": f"成功上传 {len(files)} 张图片",
                "images": uploaded_images
            }
        except Exception as e:
            logger.error(f"船艇图片上传失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="图片上传失败"
            )
    
    @staticmethod
    def get_available_boats(
        db: Session,
        boat_type: Optional[BoatType] = None,
        min_capacity: Optional[int] = None,
        max_hourly_rate: Optional[float] = None,
        location: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> dict:
        """获取可用船艇列表"""
        boats = crud_boat.get_available_boats(
            db,
            boat_type=boat_type,
            min_capacity=min_capacity,
            max_hourly_rate=max_hourly_rate,
            location=location,
            skip=skip,
            limit=limit
        )
        
        # 统计总数（简化处理）
        total_boats = crud_boat.get_by_status(db, status=BoatStatus.AVAILABLE)
        total = len(total_boats)
        
        return {
            "boats": [BoatResponse.model_validate(boat).model_dump() for boat in boats],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_boats_need_maintenance(db: Session, user_id: int) -> List[dict]:
        """获取需要维护的船艇（商家）"""
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能查看维护信息"
            )
        
        boats = crud_boat.get_boats_need_maintenance(db)
        # 筛选出属于当前商家的船艇
        merchant_boats = [boat for boat in boats if boat.merchant_id == merchant.id]
        
        return [
            {
                "id": boat.id,
                "name": boat.name,
                "next_maintenance": boat.next_maintenance,
                "status": boat.status
            }
            for boat in merchant_boats
        ] 
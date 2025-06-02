from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
import json
from app.crud.service import crud_service
from app.crud.merchant import crud_merchant
from app.crud.boat import crud_boat
from app.schemas.service import (
    ServiceCreate, ServiceUpdate, ServiceResponse, ServiceListResponse, 
    ServiceStatusUpdate, ServiceScheduleUpdate, ServiceSearchFilter
)
from app.models.service import ServiceStatus, ServiceType
from app.models.merchant import MerchantStatus
from app.models.boat import BoatStatus
from app.utils.logger import logger
from app.utils.file_handler import upload_image


class ServiceService:
    """服务业务逻辑类"""
    
    @staticmethod
    def create_service(db: Session, user_id: int, service_create: ServiceCreate) -> ServiceResponse:
        """创建服务"""
        # 检查用户是否有商家资质
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能发布服务"
            )
        
        if merchant.status != MerchantStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="商家状态异常，无法发布服务"
            )
        
        # 如果关联船艇，检查船艇是否属于该商家且可用
        if service_create.boat_id:
            boat = crud_boat.get(db, id=service_create.boat_id)
            if not boat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="指定的船艇不存在"
                )
            
            if boat.merchant_id != merchant.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能使用自己的船艇"
                )
            
            if boat.status not in [BoatStatus.AVAILABLE]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="船艇状态不可用"
                )
        
        # 准备服务数据
        service_data = service_create.model_dump()
        service_data["merchant_id"] = merchant.id
        
        # 处理JSON字段
        if service_create.includes:
            service_data["includes"] = json.dumps(service_create.includes, ensure_ascii=False)
        if service_create.excludes:
            service_data["excludes"] = json.dumps(service_create.excludes, ensure_ascii=False)
        if service_create.requirements:
            service_data["requirements"] = json.dumps(service_create.requirements, ensure_ascii=False)
        if service_create.available_times:
            service_data["available_times"] = json.dumps(service_create.available_times, ensure_ascii=False)
        
        service = crud_service.create(db, obj_in=service_data)
        
        logger.info(f"服务创建成功: {service.title}, 商家ID: {merchant.id}")
        
        return ServiceResponse.model_validate(service)
    
    @staticmethod
    def get_merchant_services(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[ServiceStatus] = None,
        service_type: Optional[ServiceType] = None
    ) -> dict:
        """获取商家的服务列表"""
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能查看服务列表"
            )
        
        services = crud_service.get_by_merchant(db, merchant_id=merchant.id, skip=skip, limit=limit)
        
        # 应用筛选条件
        if status or service_type:
            filtered_services = []
            for service in services:
                if status and service.status != status:
                    continue
                if service_type and service.service_type != service_type:
                    continue
                filtered_services.append(service)
            services = filtered_services
        
        total = crud_service.get_merchant_service_count(db, merchant_id=merchant.id)
        
        return {
            "services": [ServiceResponse.model_validate(service).model_dump() for service in services],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_service_detail(db: Session, service_id: int) -> ServiceResponse:
        """获取服务详情"""
        service = crud_service.get(db, id=service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务不存在"
            )
        
        return ServiceResponse.model_validate(service)
    
    @staticmethod
    def update_service(db: Session, user_id: int, service_id: int, service_update: ServiceUpdate) -> ServiceResponse:
        """更新服务信息"""
        service = crud_service.get(db, id=service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务不存在"
            )
        
        # 检查权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant or merchant.id != service.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改此服务"
            )
        
        # 如果更新船艇关联，检查船艇权限
        if service_update.boat_id:
            boat = crud_boat.get(db, id=service_update.boat_id)
            if not boat or boat.merchant_id != merchant.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能使用自己的船艇"
                )
        
        # 处理JSON字段
        update_data = service_update.model_dump(exclude_unset=True)
        if service_update.includes is not None:
            update_data["includes"] = json.dumps(service_update.includes, ensure_ascii=False)
        if service_update.excludes is not None:
            update_data["excludes"] = json.dumps(service_update.excludes, ensure_ascii=False)
        if service_update.requirements is not None:
            update_data["requirements"] = json.dumps(service_update.requirements, ensure_ascii=False)
        if service_update.available_times is not None:
            update_data["available_times"] = json.dumps(service_update.available_times, ensure_ascii=False)
        
        updated_service = crud_service.update(db, db_obj=service, obj_in=update_data)
        
        logger.info(f"服务信息更新: {service.title}")
        
        return ServiceResponse.model_validate(updated_service)
    
    @staticmethod
    def delete_service(db: Session, user_id: int, service_id: int) -> dict:
        """删除服务"""
        service = crud_service.get(db, id=service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务不存在"
            )
        
        # 检查权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant or merchant.id != service.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限删除此服务"
            )
        
        # 检查是否有进行中的订单
        # TODO: 实现订单检查逻辑
        
        crud_service.remove(db, id=service_id)
        
        logger.info(f"服务删除成功: {service.title}")
        
        return {"message": f"服务 {service.title} 删除成功"}
    
    @staticmethod
    def update_service_status(db: Session, user_id: int, service_id: int, status_update: ServiceStatusUpdate) -> dict:
        """更新服务状态"""
        service = crud_service.get(db, id=service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务不存在"
            )
        
        # 检查权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant or merchant.id != service.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改此服务状态"
            )
        
        updated_service = crud_service.update_status(
            db, service_id=service_id, status=status_update.status
        )
        
        logger.info(f"服务状态更新: {service.title} -> {status_update.status}")
        
        return {
            "message": "服务状态更新成功",
            "service_id": service_id,
            "new_status": status_update.status
        }
    
    @staticmethod
    def update_service_schedule(db: Session, user_id: int, service_id: int, schedule_update: ServiceScheduleUpdate) -> dict:
        """更新服务排期"""
        service = crud_service.get(db, id=service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务不存在"
            )
        
        # 检查权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant or merchant.id != service.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改此服务排期"
            )
        
        update_data = {
            "available_times": json.dumps(schedule_update.available_times, ensure_ascii=False)
        }
        if schedule_update.advance_booking_hours:
            update_data["advance_booking_hours"] = schedule_update.advance_booking_hours
        
        updated_service = crud_service.update(db, db_obj=service, obj_in=update_data)
        
        logger.info(f"服务排期更新: {service.title}")
        
        return {"message": "服务排期更新成功"}
    
    @staticmethod
    async def upload_service_images(db: Session, user_id: int, service_id: int, files: List[UploadFile]) -> dict:
        """上传服务图片"""
        service = crud_service.get(db, id=service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务不存在"
            )
        
        # 检查权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant or merchant.id != service.merchant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限上传此服务图片"
            )
        
        try:
            uploaded_images = []
            for file in files:
                file_info = await upload_image(file, folder="services")
                uploaded_images.append({
                    "url": file_info["file_url"],
                    "thumbnail": file_info.get("thumbnail_url")
                })
            
            # 更新服务图片信息
            existing_images = json.loads(service.images) if service.images else []
            existing_images.extend(uploaded_images)
            
            crud_service.update(db, db_obj=service, obj_in={"images": json.dumps(existing_images, ensure_ascii=False)})
            
            logger.info(f"服务图片上传成功: {service.title}, 上传 {len(files)} 张图片")
            
            return {
                "message": f"成功上传 {len(files)} 张图片",
                "images": uploaded_images
            }
        except Exception as e:
            logger.error(f"服务图片上传失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="图片上传失败"
            )
    
    @staticmethod
    def get_available_services(
        db: Session,
        filter_params: ServiceSearchFilter,
        skip: int = 0,
        limit: int = 100
    ) -> dict:
        """获取可预订服务列表"""
        if filter_params.keyword:
            services = crud_service.search_services(
                db, keyword=filter_params.keyword, skip=skip, limit=limit
            )
        else:
            services = crud_service.get_active_services(
                db,
                service_type=filter_params.service_type,
                min_price=float(filter_params.min_price) if filter_params.min_price else None,
                max_price=float(filter_params.max_price) if filter_params.max_price else None,
                max_participants=filter_params.max_participants,
                region_id=filter_params.region_id,
                is_green_service=filter_params.is_green_service,
                skip=skip,
                limit=limit
            )
        
        # 统计总数（简化处理）
        total_services = crud_service.get_by_status(db, status=ServiceStatus.ACTIVE)
        total = len(total_services)
        
        return {
            "services": [ServiceResponse.model_validate(service).model_dump() for service in services],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_featured_services(db: Session, skip: int = 0, limit: int = 100) -> dict:
        """获取推荐服务"""
        services = crud_service.get_featured_services(db, skip=skip, limit=limit)
        
        return {
            "services": [ServiceResponse.model_validate(service).model_dump() for service in services],
            "total": len(services)
        }
    
    @staticmethod
    def get_green_services(db: Session, skip: int = 0, limit: int = 100) -> dict:
        """获取绿色服务"""
        services = crud_service.get_green_services(db, skip=skip, limit=limit)
        
        return {
            "services": [ServiceResponse.model_validate(service).model_dump() for service in services],
            "total": len(services)
        }
    
    @staticmethod
    def get_popular_services(db: Session, skip: int = 0, limit: int = 100) -> dict:
        """获取热门服务"""
        services = crud_service.get_popular_services(db, skip=skip, limit=limit)
        
        return {
            "services": [ServiceResponse.model_validate(service).model_dump() for service in services],
            "total": len(services)
        } 
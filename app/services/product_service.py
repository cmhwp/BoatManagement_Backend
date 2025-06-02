from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from decimal import Decimal
import json
from datetime import datetime, date

from app.crud.product import crud_product, crud_inventory_log, crud_service_product_bundle
from app.crud.merchant import crud_merchant
from app.crud.user import crud_user
from app.crud.service import crud_service
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    InventoryLogCreate, InventoryLogResponse, ProductSearchFilter,
    ProductStatistics, ProductBundleCreate, ProductBundleResponse,
    ProductStatus, ProductCategory, InventoryOperation
)
from app.models.user import UserRole
from app.utils.logger import logger
from app.utils.file_handler import upload_image


class ProductService:
    """农产品业务逻辑类"""
    
    @staticmethod
    def create_product(db: Session, user_id: int, product_create: ProductCreate) -> ProductResponse:
        """创建农产品"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能创建农产品"
            )
        
        # 处理认证和标签数据
        product_data = product_create.model_dump()
        product_data["merchant_id"] = merchant.id
        product_data["status"] = ProductStatus.ACTIVE
        product_data["average_rating"] = 0.0
        product_data["review_count"] = 0
        product_data["sales_count"] = 0
        product_data["images"] = json.dumps([], ensure_ascii=False)
        
        # 处理认证列表
        if product_create.certifications:
            product_data["certifications"] = json.dumps([cert.value for cert in product_create.certifications], ensure_ascii=False)
        else:
            product_data["certifications"] = json.dumps([], ensure_ascii=False)
        
        # 处理标签列表
        if product_create.tags:
            product_data["tags"] = json.dumps(product_create.tags, ensure_ascii=False)
        else:
            product_data["tags"] = json.dumps([], ensure_ascii=False)
        
        # 处理营养信息
        if product_create.nutritional_info:
            product_data["nutritional_info"] = json.dumps(product_create.nutritional_info, ensure_ascii=False)
        
        product = crud_product.create(db, obj_in=product_data)
        
        # 创建初始库存记录
        if product_create.stock_quantity > 0:
            inventory_log_data = InventoryLogCreate(
                product_id=product.id,
                operation_type=InventoryOperation.IN,
                quantity=product_create.stock_quantity,
                unit_cost=product_create.cost_price,
                reason="初始库存"
            )
            crud_inventory_log.create_with_product_update(
                db, 
                obj_in=inventory_log_data, 
                operator_id=user_id
            )
        
        logger.info(f"农产品创建成功: 商家{merchant.id}创建产品{product.name}")
        
        return ProductResponse.model_validate(product)
    
    @staticmethod
    def get_merchant_products(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> dict:
        """获取商家的农产品列表"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能查看产品列表"
            )
        
        products = crud_product.get_by_merchant_id(
            db, merchant_id=merchant.id, skip=skip, limit=limit
        )
        
        # 计算总数
        all_products = crud_product.get_by_merchant_id(db, merchant_id=merchant.id, skip=0, limit=1000)
        total = len(all_products)
        
        return {
            "products": [ProductListResponse.model_validate(product).model_dump() for product in products],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_public_products(
        db: Session,
        filter_params: ProductSearchFilter,
        skip: int = 0,
        limit: int = 100
    ) -> dict:
        """获取公开的农产品列表"""
        products = crud_product.search_products(
            db,
            filter_params=filter_params,
            skip=skip,
            limit=limit
        )
        
        # 简化处理，获取总数
        all_products = crud_product.search_products(
            db,
            filter_params=filter_params,
            skip=0,
            limit=1000
        )
        total = len(all_products)
        
        return {
            "products": [ProductListResponse.model_validate(product).model_dump() for product in products],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_product_detail(db: Session, product_id: int) -> ProductResponse:
        """获取农产品详情"""
        product = crud_product.get(db, id=product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="农产品不存在"
            )
        
        # 只显示上架的产品给公众
        if product.status != ProductStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="农产品暂不可用"
            )
        
        # 获取关联的库存日志
        inventory_logs = crud_inventory_log.get_by_product_id(db, product_id=product_id, limit=10)
        
        response = ProductResponse.model_validate(product)
        response.inventory_logs = [InventoryLogResponse.model_validate(log).model_dump() for log in inventory_logs]
        
        return response
    
    @staticmethod
    def get_merchant_product_detail(db: Session, user_id: int, product_id: int) -> ProductResponse:
        """商家获取农产品详情（包含成本等敏感信息）"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能查看详细信息"
            )
        
        product = crud_product.get(db, id=product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="农产品不存在"
            )
        
        # 检查产品所有权
        if product.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限查看此农产品"
            )
        
        # 获取关联的库存日志
        inventory_logs = crud_inventory_log.get_by_product_id(db, product_id=product_id, limit=20)
        
        response = ProductResponse.model_validate(product)
        response.inventory_logs = [InventoryLogResponse.model_validate(log).model_dump() for log in inventory_logs]
        
        return response
    
    @staticmethod
    def update_product(db: Session, user_id: int, product_id: int, product_update: ProductUpdate) -> ProductResponse:
        """更新农产品信息"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能更新农产品"
            )
        
        product = crud_product.get(db, id=product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="农产品不存在"
            )
        
        # 检查产品所有权
        if product.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限更新此农产品"
            )
        
        # 处理更新数据
        update_data = product_update.model_dump(exclude_unset=True)
        
        # 处理认证列表
        if product_update.certifications is not None:
            update_data["certifications"] = json.dumps([cert.value for cert in product_update.certifications], ensure_ascii=False)
        
        # 处理标签列表
        if product_update.tags is not None:
            update_data["tags"] = json.dumps(product_update.tags, ensure_ascii=False)
        
        # 处理营养信息
        if product_update.nutritional_info is not None:
            update_data["nutritional_info"] = json.dumps(product_update.nutritional_info, ensure_ascii=False)
        
        # 如果更新了库存，需要记录日志
        if product_update.stock_quantity is not None and product_update.stock_quantity != product.stock_quantity:
            quantity_change = product_update.stock_quantity - product.stock_quantity
            inventory_log_data = InventoryLogCreate(
                product_id=product_id,
                operation_type=InventoryOperation.ADJUST,
                quantity=quantity_change,
                reason="库存调整"
            )
            crud_inventory_log.create_with_product_update(
                db, 
                obj_in=inventory_log_data, 
                operator_id=user_id
            )
            # 从更新数据中移除库存字段，因为已经通过库存日志更新
            update_data.pop("stock_quantity", None)
        
        updated_product = crud_product.update(db, db_obj=product, obj_in=update_data)
        
        logger.info(f"农产品更新: 商家{merchant.id}更新产品{product_id}")
        
        return ProductResponse.model_validate(updated_product)
    
    @staticmethod
    def delete_product(db: Session, user_id: int, product_id: int) -> dict:
        """删除农产品"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能删除农产品"
            )
        
        product = crud_product.get(db, id=product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="农产品不存在"
            )
        
        # 检查产品所有权
        if product.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限删除此农产品"
            )
        
        # 软删除：设置为停产状态
        crud_product.update(db, db_obj=product, obj_in={"status": ProductStatus.DISCONTINUED})
        
        logger.info(f"农产品删除: 商家{merchant.id}删除产品{product_id}")
        
        return {"message": "农产品删除成功"}
    
    @staticmethod
    def get_featured_products(db: Session, skip: int = 0, limit: int = 100) -> dict:
        """获取推荐农产品"""
        products = crud_product.get_featured_products(db, skip=skip, limit=limit)
        
        return {
            "products": [ProductListResponse.model_validate(product).model_dump() for product in products],
            "total": len(products)
        }
    
    @staticmethod
    def get_seasonal_products(db: Session, skip: int = 0, limit: int = 100) -> dict:
        """获取当季农产品"""
        current_month = datetime.now().month
        products = crud_product.get_seasonal_products(db, current_month=current_month, skip=skip, limit=limit)
        
        return {
            "products": [ProductListResponse.model_validate(product).model_dump() for product in products],
            "total": len(products)
        }
    
    @staticmethod
    def get_products_by_category(db: Session, category: ProductCategory, skip: int = 0, limit: int = 100) -> dict:
        """根据分类获取农产品"""
        products = crud_product.get_by_category(db, category=category, skip=skip, limit=limit)
        
        # 简化处理，获取总数
        all_products = crud_product.get_by_category(db, category=category, skip=0, limit=1000)
        total = len(all_products)
        
        return {
            "products": [ProductListResponse.model_validate(product).model_dump() for product in products],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_low_stock_products(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> dict:
        """获取低库存农产品（商家专用）"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能查看库存预警"
            )
        
        products = crud_product.get_low_stock_products(
            db, merchant_id=merchant.id, skip=skip, limit=limit
        )
        
        return {
            "products": [ProductListResponse.model_validate(product).model_dump() for product in products],
            "total": len(products)
        }
    
    @staticmethod
    def manage_inventory(db: Session, user_id: int, inventory_create: InventoryLogCreate) -> InventoryLogResponse:
        """管理库存（入库、出库、调整等）"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能管理库存"
            )
        
        # 检查产品是否存在且属于该商家
        product = crud_product.get(db, id=inventory_create.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="农产品不存在"
            )
        
        if product.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限管理此农产品库存"
            )
        
        # 检查出库操作的库存是否足够
        if inventory_create.operation_type in [InventoryOperation.OUT, InventoryOperation.DAMAGED, InventoryOperation.EXPIRED]:
            required_quantity = abs(inventory_create.quantity)
            if product.stock_quantity < required_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"库存不足，当前库存: {product.stock_quantity}, 需要: {required_quantity}"
                )
        
        inventory_log = crud_inventory_log.create_with_product_update(
            db, 
            obj_in=inventory_create, 
            operator_id=user_id
        )
        
        logger.info(f"库存操作: 商家{merchant.id}对产品{inventory_create.product_id}执行{inventory_create.operation_type}操作，数量{inventory_create.quantity}")
        
        return InventoryLogResponse.model_validate(inventory_log)
    
    @staticmethod
    def get_inventory_logs(db: Session, user_id: int, product_id: int, skip: int = 0, limit: int = 100) -> dict:
        """获取产品库存日志"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能查看库存日志"
            )
        
        # 检查产品所有权
        product = crud_product.get(db, id=product_id)
        if not product or product.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限查看此农产品库存日志"
            )
        
        logs = crud_inventory_log.get_by_product_id(db, product_id=product_id, skip=skip, limit=limit)
        
        # 简化处理，获取总数
        all_logs = crud_inventory_log.get_by_product_id(db, product_id=product_id, skip=0, limit=1000)
        total = len(all_logs)
        
        return {
            "logs": [InventoryLogResponse.model_validate(log).model_dump() for log in logs],
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
            "pages": (total + limit - 1) // limit
        }
    
    @staticmethod
    def get_product_statistics(db: Session, user_id: int) -> ProductStatistics:
        """获取农产品统计信息"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能查看产品统计"
            )
        
        stats = crud_product.get_product_statistics(db, merchant_id=merchant.id)
        
        # 获取最近的库存活动
        recent_activities = crud_inventory_log.get_recent_activities(
            db, merchant_id=merchant.id, days=7, limit=10
        )
        
        activities_data = []
        for activity in recent_activities:
            activities_data.append({
                "date": activity.created_at.isoformat(),
                "operation": activity.operation_type,
                "product_name": activity.product.name if activity.product else "未知产品",
                "quantity_change": activity.quantity_change,
                "reason": activity.reason
            })
        
        return ProductStatistics(
            total_products=stats["total_products"],
            active_products=stats["active_products"],
            out_of_stock_products=stats["out_of_stock_products"],
            low_stock_products=stats["low_stock_products"],
            total_inventory_value=Decimal(str(stats["total_inventory_value"])),
            category_distribution=stats["category_distribution"],
            sales_summary=stats["sales_summary"],
            recent_activities=activities_data
        )
    
    @staticmethod
    async def upload_product_images(db: Session, user_id: int, product_id: int, files: List[UploadFile]) -> dict:
        """上传农产品图片"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能上传产品图片"
            )
        
        product = crud_product.get(db, id=product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="农产品不存在"
            )
        
        # 检查产品所有权
        if product.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限上传此农产品图片"
            )
        
        try:
            uploaded_files = []
            for file in files:
                file_info = await upload_image(file, folder="products")
                uploaded_files.append(file_info["file_url"])
            
            # 更新产品图片信息
            existing_images = json.loads(product.images) if product.images else []
            existing_images.extend(uploaded_files)
            
            crud_product.update(db, db_obj=product, obj_in={"images": json.dumps(existing_images, ensure_ascii=False)})
            
            logger.info(f"产品图片上传成功: 产品{product_id}, 上传 {len(files)} 个文件")
            
            return {
                "message": f"成功上传 {len(files)} 个图片",
                "images": uploaded_files
            }
        except Exception as e:
            logger.error(f"产品图片上传失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="图片上传失败"
            )
    
    @staticmethod
    def create_product_bundle(db: Session, user_id: int, bundle_create: ProductBundleCreate) -> ProductBundleResponse:
        """创建服务-产品组合"""
        # 检查商家权限
        merchant = crud_merchant.get_by_user_id(db, user_id=user_id)
        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有商家才能创建产品组合"
            )
        
        # 检查服务是否存在且属于该商家
        service = crud_service.get(db, id=bundle_create.service_id)
        if not service or service.merchant_id != merchant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限为此服务创建产品组合"
            )
        
        # 检查产品是否都属于该商家
        for product_id in bundle_create.product_ids:
            product = crud_product.get(db, id=product_id)
            if not product or product.merchant_id != merchant.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"产品{product_id}不属于当前商家"
                )
        
        bundle = crud_service_product_bundle.create_bundle(
            db,
            service_id=bundle_create.service_id,
            product_ids=bundle_create.product_ids,
            bundle_price=float(bundle_create.bundle_price) if bundle_create.bundle_price else None,
            description=bundle_create.description
        )
        
        logger.info(f"产品组合创建成功: 商家{merchant.id}为服务{bundle_create.service_id}创建产品组合")
        
        return ProductBundleResponse.model_validate(bundle) 
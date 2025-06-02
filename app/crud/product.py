from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from datetime import datetime, date
import json

from app.crud.base import CRUDBase
from app.models.product import AgriculturalProduct, InventoryLog, ServiceProductBundle
from app.schemas.product import (
    ProductCreate, ProductUpdate, InventoryLogCreate, ProductSearchFilter,
    ProductStatus, ProductCategory, InventoryOperation, QualityCertification
)


class CRUDProduct(CRUDBase[AgriculturalProduct, ProductCreate, ProductUpdate]):
    """农产品CRUD操作类"""
    
    def get_by_merchant_id(
        self, 
        db: Session, 
        *, 
        merchant_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AgriculturalProduct]:
        """获取商家的农产品列表"""
        return (
            db.query(AgriculturalProduct)
            .filter(AgriculturalProduct.merchant_id == merchant_id)
            .order_by(desc(AgriculturalProduct.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_category(
        self, 
        db: Session, 
        *, 
        category: ProductCategory, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AgriculturalProduct]:
        """根据分类查询农产品"""
        return (
            db.query(AgriculturalProduct)
            .filter(
                and_(
                    AgriculturalProduct.category == category,
                    AgriculturalProduct.status == ProductStatus.ACTIVE
                )
            )
            .order_by(desc(AgriculturalProduct.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_status(
        self, 
        db: Session, 
        *, 
        status: ProductStatus,
        merchant_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[AgriculturalProduct]:
        """根据状态查询农产品"""
        query = db.query(AgriculturalProduct).filter(AgriculturalProduct.status == status)
        
        if merchant_id:
            query = query.filter(AgriculturalProduct.merchant_id == merchant_id)
            
        return (
            query
            .order_by(desc(AgriculturalProduct.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_featured_products(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AgriculturalProduct]:
        """获取推荐农产品"""
        return (
            db.query(AgriculturalProduct)
            .filter(
                and_(
                    AgriculturalProduct.is_featured == True,
                    AgriculturalProduct.status == ProductStatus.ACTIVE
                )
            )
            .order_by(desc(AgriculturalProduct.average_rating), desc(AgriculturalProduct.sales_count))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_seasonal_products(
        self, 
        db: Session, 
        *, 
        current_month: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[AgriculturalProduct]:
        """获取当前季节的农产品"""
        return (
            db.query(AgriculturalProduct)
            .filter(
                and_(
                    AgriculturalProduct.is_seasonal == True,
                    AgriculturalProduct.status == ProductStatus.ACTIVE,
                    or_(
                        and_(
                            AgriculturalProduct.season_start <= current_month,
                            AgriculturalProduct.season_end >= current_month
                        ),
                        and_(
                            AgriculturalProduct.season_start > AgriculturalProduct.season_end,  # 跨年季节
                            or_(
                                AgriculturalProduct.season_start <= current_month,
                                AgriculturalProduct.season_end >= current_month
                            )
                        )
                    )
                )
            )
            .order_by(desc(AgriculturalProduct.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_low_stock_products(
        self, 
        db: Session, 
        *, 
        merchant_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[AgriculturalProduct]:
        """获取低库存农产品"""
        query = db.query(AgriculturalProduct).filter(
            AgriculturalProduct.stock_quantity <= AgriculturalProduct.min_stock_alert
        )
        
        if merchant_id:
            query = query.filter(AgriculturalProduct.merchant_id == merchant_id)
            
        return (
            query
            .order_by(asc(AgriculturalProduct.stock_quantity))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_products(
        self,
        db: Session,
        *,
        filter_params: ProductSearchFilter,
        merchant_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgriculturalProduct]:
        """搜索农产品"""
        query = db.query(AgriculturalProduct)
        
        # 商家筛选
        if merchant_id:
            query = query.filter(AgriculturalProduct.merchant_id == merchant_id)
        
        # 分类筛选
        if filter_params.category:
            query = query.filter(AgriculturalProduct.category == filter_params.category)
        
        # 状态筛选
        if filter_params.status:
            query = query.filter(AgriculturalProduct.status == filter_params.status)
        else:
            # 默认只显示在售产品
            query = query.filter(AgriculturalProduct.status == ProductStatus.ACTIVE)
        
        # 价格范围筛选
        if filter_params.min_price:
            query = query.filter(AgriculturalProduct.price >= filter_params.min_price)
        if filter_params.max_price:
            query = query.filter(AgriculturalProduct.price <= filter_params.max_price)
        
        # 库存筛选
        if filter_params.has_stock is not None:
            if filter_params.has_stock:
                query = query.filter(AgriculturalProduct.stock_quantity > 0)
            else:
                query = query.filter(AgriculturalProduct.stock_quantity == 0)
        
        # 推荐筛选
        if filter_params.is_featured is not None:
            query = query.filter(AgriculturalProduct.is_featured == filter_params.is_featured)
        
        # 季节性筛选
        if filter_params.is_seasonal is not None:
            query = query.filter(AgriculturalProduct.is_seasonal == filter_params.is_seasonal)
        
        # 认证筛选
        if filter_params.certifications:
            for cert in filter_params.certifications:
                query = query.filter(AgriculturalProduct.certifications.contains(cert))
        
        # 产地筛选
        if filter_params.origin_location:
            query = query.filter(AgriculturalProduct.origin_location.contains(filter_params.origin_location))
        
        # 关键词搜索
        if filter_params.keyword:
            keyword = f"%{filter_params.keyword}%"
            query = query.filter(
                or_(
                    AgriculturalProduct.name.like(keyword),
                    AgriculturalProduct.description.like(keyword),
                    AgriculturalProduct.tags.like(keyword),
                    AgriculturalProduct.origin_location.like(keyword)
                )
            )
        
        # 排序
        if filter_params.sort_by and filter_params.sort_order:
            sort_column = getattr(AgriculturalProduct, filter_params.sort_by, None)
            if sort_column:
                if filter_params.sort_order.lower() == "asc":
                    query = query.order_by(asc(sort_column))
                else:
                    query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(desc(AgriculturalProduct.created_at))
        else:
            query = query.order_by(desc(AgriculturalProduct.created_at))
        
        return query.offset(skip).limit(limit).all()
    
    def get_product_statistics(
        self, 
        db: Session, 
        *, 
        merchant_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取产品统计信息"""
        query = db.query(AgriculturalProduct)
        if merchant_id:
            query = query.filter(AgriculturalProduct.merchant_id == merchant_id)
        
        products = query.all()
        
        if not products:
            return {
                "total_products": 0,
                "active_products": 0,
                "out_of_stock_products": 0,
                "low_stock_products": 0,
                "total_inventory_value": 0,
                "category_distribution": {},
                "sales_summary": {}
            }
        
        total_products = len(products)
        active_products = len([p for p in products if p.status == ProductStatus.ACTIVE])
        out_of_stock_products = len([p for p in products if p.stock_quantity == 0])
        low_stock_products = len([p for p in products if p.stock_quantity <= p.min_stock_alert])
        
        # 计算库存总价值
        total_inventory_value = sum(
            float(p.cost_price or p.price) * p.stock_quantity for p in products
        )
        
        # 分类分布
        category_distribution = {}
        for product in products:
            category = product.category
            category_distribution[category] = category_distribution.get(category, 0) + 1
        
        # 销售统计
        total_sales = sum(p.sales_count for p in products)
        avg_rating = sum(p.average_rating for p in products) / len(products) if products else 0
        
        sales_summary = {
            "total_sales": total_sales,
            "average_rating": round(avg_rating, 2),
            "top_selling_products": sorted(products, key=lambda x: x.sales_count, reverse=True)[:5]
        }
        
        return {
            "total_products": total_products,
            "active_products": active_products,
            "out_of_stock_products": out_of_stock_products,
            "low_stock_products": low_stock_products,
            "total_inventory_value": total_inventory_value,
            "category_distribution": category_distribution,
            "sales_summary": sales_summary
        }
    
    def update_stock(self, db: Session, *, product_id: int, quantity_change: int) -> Optional[AgriculturalProduct]:
        """更新库存数量"""
        product = self.get(db, id=product_id)
        if product:
            new_stock = max(0, product.stock_quantity + quantity_change)
            
            # 根据库存状态更新产品状态
            if new_stock == 0 and product.status == ProductStatus.ACTIVE:
                status = ProductStatus.OUT_OF_STOCK
            elif new_stock > 0 and product.status == ProductStatus.OUT_OF_STOCK:
                status = ProductStatus.ACTIVE
            else:
                status = product.status
            
            return self.update(
                db, 
                db_obj=product, 
                obj_in={"stock_quantity": new_stock, "status": status}
            )
        return None
    
    def update_rating(self, db: Session, *, product_id: int, new_rating: float, review_count: int) -> Optional[AgriculturalProduct]:
        """更新产品评分"""
        product = self.get(db, id=product_id)
        if product:
            return self.update(
                db,
                db_obj=product,
                obj_in={
                    "average_rating": new_rating,
                    "review_count": review_count
                }
            )
        return None
    
    def increment_sales(self, db: Session, *, product_id: int, sales_increment: int = 1) -> Optional[AgriculturalProduct]:
        """增加销售数量"""
        product = self.get(db, id=product_id)
        if product:
            return self.update(
                db,
                db_obj=product,
                obj_in={"sales_count": product.sales_count + sales_increment}
            )
        return None


class CRUDInventoryLog(CRUDBase[InventoryLog, InventoryLogCreate, dict]):
    """库存日志CRUD操作类"""
    
    def create_with_product_update(
        self, 
        db: Session, 
        *, 
        obj_in: InventoryLogCreate,
        operator_id: int
    ) -> InventoryLog:
        """创建库存日志并更新产品库存"""
        # 获取产品当前库存
        product_crud = CRUDProduct(AgriculturalProduct)
        product = product_crud.get(db, id=obj_in.product_id)
        if not product:
            raise ValueError("产品不存在")
        
        stock_before = product.stock_quantity
        stock_after = max(0, stock_before + obj_in.quantity)
        
        # 计算总成本
        total_cost = None
        if obj_in.unit_cost:
            total_cost = obj_in.unit_cost * abs(obj_in.quantity)
        
        # 创建库存日志
        log_data = {
            "product_id": obj_in.product_id,
            "operation_type": obj_in.operation_type,
            "quantity_change": obj_in.quantity,
            "unit_cost": obj_in.unit_cost,
            "total_cost": total_cost,
            "stock_before": stock_before,
            "stock_after": stock_after,
            "reason": obj_in.reason,
            "reference_no": obj_in.reference_no,
            "operator_id": operator_id
        }
        
        inventory_log = self.create(db, obj_in=log_data)
        
        # 更新产品库存
        product_crud.update_stock(db, product_id=obj_in.product_id, quantity_change=obj_in.quantity)
        
        return inventory_log
    
    def get_by_product_id(
        self, 
        db: Session, 
        *, 
        product_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[InventoryLog]:
        """获取产品的库存日志"""
        return (
            db.query(InventoryLog)
            .filter(InventoryLog.product_id == product_id)
            .order_by(desc(InventoryLog.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_operation_type(
        self, 
        db: Session, 
        *, 
        operation_type: InventoryOperation,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[InventoryLog]:
        """根据操作类型查询库存日志"""
        query = db.query(InventoryLog).filter(InventoryLog.operation_type == operation_type)
        
        if start_date:
            query = query.filter(InventoryLog.created_at >= start_date)
        if end_date:
            query = query.filter(InventoryLog.created_at <= end_date)
        
        return (
            query
            .order_by(desc(InventoryLog.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_recent_activities(
        self, 
        db: Session, 
        *, 
        merchant_id: Optional[int] = None,
        days: int = 7,
        limit: int = 50
    ) -> List[InventoryLog]:
        """获取最近的库存活动"""
        from datetime import timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        query = db.query(InventoryLog).filter(InventoryLog.created_at >= start_date)
        
        if merchant_id:
            query = query.join(AgriculturalProduct).filter(AgriculturalProduct.merchant_id == merchant_id)
        
        return (
            query
            .order_by(desc(InventoryLog.created_at))
            .limit(limit)
            .all()
        )


class CRUDServiceProductBundle(CRUDBase[ServiceProductBundle, dict, dict]):
    """服务产品组合CRUD操作类"""
    
    def get_by_service_id(self, db: Session, *, service_id: int) -> Optional[ServiceProductBundle]:
        """根据服务ID获取产品组合"""
        return db.query(ServiceProductBundle).filter(ServiceProductBundle.service_id == service_id).first()
    
    def create_bundle(
        self, 
        db: Session, 
        *, 
        service_id: int,
        product_ids: List[int],
        bundle_price: Optional[float] = None,
        description: Optional[str] = None
    ) -> ServiceProductBundle:
        """创建服务产品组合"""
        bundle_data = {
            "service_id": service_id,
            "bundle_price": bundle_price,
            "description": description
        }
        
        bundle = self.create(db, obj_in=bundle_data)
        
        # 创建关联关系（这里简化处理，实际需要通过关系表）
        # 在真实实现中，需要处理多对多关系
        
        return bundle
    
    def remove_bundle(self, db: Session, *, service_id: int) -> bool:
        """删除服务产品组合"""
        bundle = self.get_by_service_id(db, service_id=service_id)
        if bundle:
            self.remove(db, id=bundle.id)
            return True
        return False


# 创建CRUD实例
crud_product = CRUDProduct(AgriculturalProduct)
crud_inventory_log = CRUDInventoryLog(InventoryLog)
crud_service_product_bundle = CRUDServiceProductBundle(ServiceProductBundle) 
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.database import get_db
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductSearchFilter,
    InventoryLogCreate, InventoryLogResponse, ProductStatistics,
    ProductBundleCreate, ProductBundleResponse, ProductCategory
)
from app.services.product_service import ProductService
from app.utils.response import success_response, error_response, paginated_response
from app.utils.dependencies import get_current_user, require_merchant

router = APIRouter()


@router.post("", summary="创建农产品")
async def create_product(
    product_create: ProductCreate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """创建农产品（商家专用）"""
    try:
        result = ProductService.create_product(db, current_user.id, product_create)
        return success_response(
            message="农产品创建成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/my-products", summary="获取我的农产品")
async def get_my_products(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取商家的农产品列表"""
    try:
        skip = (page - 1) * size
        result = ProductService.get_merchant_products(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["products"],
            total=result["total"],
            page=page,
            size=size,
            message="获取农产品列表成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/search", summary="搜索农产品")
async def search_products(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[ProductCategory] = Query(None, description="产品分类"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    has_stock: Optional[bool] = Query(None, description="是否有库存"),
    is_featured: Optional[bool] = Query(None, description="是否推荐"),
    is_seasonal: Optional[bool] = Query(None, description="是否季节性"),
    origin_location: Optional[str] = Query(None, description="产地"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: Optional[str] = Query("created_at", description="排序字段"),
    sort_order: Optional[str] = Query("desc", description="排序方向"),
    db: Session = Depends(get_db)
):
    """搜索农产品"""
    try:
        skip = (page - 1) * size
        
        filter_params = ProductSearchFilter(
            category=category,
            min_price=min_price,
            max_price=max_price,
            has_stock=has_stock,
            is_featured=is_featured,
            is_seasonal=is_seasonal,
            origin_location=origin_location,
            keyword=keyword,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        result = ProductService.get_public_products(
            db=db,
            filter_params=filter_params,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["products"],
            total=result["total"],
            page=page,
            size=size,
            message="搜索农产品成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/featured", summary="获取推荐农产品")
async def get_featured_products(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取推荐农产品"""
    try:
        skip = (page - 1) * size
        result = ProductService.get_featured_products(db, skip=skip, limit=size)
        
        return success_response(
            message="获取推荐农产品成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/seasonal", summary="获取当季农产品")
async def get_seasonal_products(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取当季农产品"""
    try:
        skip = (page - 1) * size
        result = ProductService.get_seasonal_products(db, skip=skip, limit=size)
        
        return success_response(
            message="获取当季农产品成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/category/{category}", summary="按分类获取农产品")
async def get_products_by_category(
    category: ProductCategory,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """根据分类获取农产品"""
    try:
        skip = (page - 1) * size
        result = ProductService.get_products_by_category(
            db=db,
            category=category,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["products"],
            total=result["total"],
            page=page,
            size=size,
            message=f"获取{category}分类农产品成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/low-stock", summary="获取低库存农产品")
async def get_low_stock_products(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取低库存农产品（商家专用）"""
    try:
        skip = (page - 1) * size
        result = ProductService.get_low_stock_products(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=size
        )
        
        return success_response(
            message="获取低库存农产品成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/statistics", summary="获取农产品统计")
async def get_product_statistics(
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取农产品统计信息（商家专用）"""
    try:
        result = ProductService.get_product_statistics(db, current_user.id)
        return success_response(
            message="获取农产品统计成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/{product_id}", summary="获取农产品详情")
async def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db)
):
    """获取农产品详细信息（公开接口）"""
    try:
        result = ProductService.get_product_detail(db, product_id)
        return success_response(
            message="获取农产品详情成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/{product_id}/merchant", summary="商家获取农产品详情")
async def get_merchant_product_detail(
    product_id: int,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """商家获取农产品详细信息（包含成本等敏感信息）"""
    try:
        result = ProductService.get_merchant_product_detail(db, current_user.id, product_id)
        return success_response(
            message="获取农产品详情成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.put("/{product_id}", summary="更新农产品信息")
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """更新农产品信息"""
    try:
        result = ProductService.update_product(db, current_user.id, product_id, product_update)
        return success_response(
            message="农产品信息更新成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.delete("/{product_id}", summary="删除农产品")
async def delete_product(
    product_id: int,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """删除农产品"""
    try:
        result = ProductService.delete_product(db, current_user.id, product_id)
        return success_response(
            message="农产品删除成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.post("/{product_id}/upload-images", summary="上传农产品图片")
async def upload_product_images(
    product_id: int,
    files: List[UploadFile] = File(...),
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """上传农产品图片"""
    try:
        result = await ProductService.upload_product_images(db, current_user.id, product_id, files)
        return success_response(
            message="农产品图片上传成功",
            data=result
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


# 库存管理接口
@router.post("/inventory", summary="管理库存")
async def manage_inventory(
    inventory_create: InventoryLogCreate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """管理农产品库存（入库、出库、调整等）"""
    try:
        result = ProductService.manage_inventory(db, current_user.id, inventory_create)
        return success_response(
            message="库存操作成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


@router.get("/{product_id}/inventory-logs", summary="获取库存日志")
async def get_inventory_logs(
    product_id: int,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取农产品库存日志"""
    try:
        skip = (page - 1) * size
        result = ProductService.get_inventory_logs(
            db=db,
            user_id=current_user.id,
            product_id=product_id,
            skip=skip,
            limit=size
        )
        
        return paginated_response(
            data=result["logs"],
            total=result["total"],
            page=page,
            size=size,
            message="获取库存日志成功"
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)


# 产品组合接口
@router.post("/bundles", summary="创建产品组合")
async def create_product_bundle(
    bundle_create: ProductBundleCreate,
    current_user = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """创建服务-产品组合"""
    try:
        result = ProductService.create_product_bundle(db, current_user.id, bundle_create)
        return success_response(
            message="产品组合创建成功",
            data=result.model_dump()
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code) 
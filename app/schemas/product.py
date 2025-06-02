from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from enum import Enum


class ProductCategory(str, Enum):
    """农产品分类枚举"""
    FRUIT = "fruit"                    # 水果
    VEGETABLE = "vegetable"           # 蔬菜
    GRAIN = "grain"                   # 粮食
    MEAT = "meat"                     # 肉类
    SEAFOOD = "seafood"               # 水产
    DAIRY = "dairy"                   # 乳制品
    PROCESSED = "processed"           # 加工品
    HERBS = "herbs"                   # 药材
    TEA = "tea"                      # 茶叶
    SPECIALTY = "specialty"           # 特产


class ProductStatus(str, Enum):
    """农产品状态枚举"""
    ACTIVE = "active"                 # 上架销售
    INACTIVE = "inactive"             # 下架
    OUT_OF_STOCK = "out_of_stock"     # 缺货
    DISCONTINUED = "discontinued"      # 停产


class ProductUnit(str, Enum):
    """农产品单位枚举"""
    KG = "kg"                        # 千克
    G = "g"                          # 克
    L = "l"                          # 升
    ML = "ml"                        # 毫升
    PIECE = "piece"                  # 个/件
    BOX = "box"                      # 盒
    BAG = "bag"                      # 袋
    BASKET = "basket"                # 筐


class QualityCertification(str, Enum):
    """质量认证枚举"""
    ORGANIC = "organic"               # 有机认证
    GREEN = "green"                   # 绿色食品
    POLLUTION_FREE = "pollution_free" # 无公害
    GAP = "gap"                      # 良好农业规范
    HACCP = "haccp"                  # 危害分析关键控制点
    ISO = "iso"                      # ISO认证


# 农产品创建模型
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="产品名称")
    category: ProductCategory = Field(..., description="产品分类")
    description: Optional[str] = Field(None, max_length=2000, description="产品描述")
    price: Decimal = Field(..., gt=0, description="销售价格")
    cost_price: Optional[Decimal] = Field(None, ge=0, description="成本价格")
    unit: ProductUnit = Field(..., description="计量单位")
    stock_quantity: int = Field(..., ge=0, description="库存数量")
    min_stock_alert: int = Field(default=10, ge=0, description="库存预警数量")
    max_stock_limit: Optional[int] = Field(None, ge=0, description="最大库存限制")
    origin_location: Optional[str] = Field(None, max_length=200, description="产地")
    harvest_date: Optional[date] = Field(None, description="采收日期")
    shelf_life_days: Optional[int] = Field(None, gt=0, description="保质期(天)")
    storage_conditions: Optional[str] = Field(None, max_length=500, description="储存条件")
    certifications: Optional[List[QualityCertification]] = Field(default_factory=list, description="质量认证")
    tags: Optional[List[str]] = Field(default_factory=list, description="产品标签")
    nutritional_info: Optional[Dict[str, Any]] = Field(None, description="营养信息")
    is_featured: bool = Field(default=False, description="是否推荐")
    is_seasonal: bool = Field(default=False, description="是否季节性产品")
    season_start: Optional[int] = Field(None, ge=1, le=12, description="销售季开始月份")
    season_end: Optional[int] = Field(None, ge=1, le=12, description="销售季结束月份")
    
    @validator('cost_price')
    def validate_cost_price(cls, v, values):
        if v is not None and 'price' in values and v > values['price']:
            raise ValueError('成本价格不能高于销售价格')
        return v
    
    @validator('season_end')
    def validate_season(cls, v, values):
        if v is not None and 'season_start' in values and values['season_start'] is not None:
            if v < values['season_start']:
                raise ValueError('销售季结束月份不能早于开始月份')
        return v
    
    class Config:
        json_encoders = {
            Decimal: str,
            date: lambda v: v.isoformat() if v else None
        }


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[Decimal] = Field(None, gt=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    min_stock_alert: Optional[int] = Field(None, ge=0)
    max_stock_limit: Optional[int] = Field(None, ge=0)
    origin_location: Optional[str] = Field(None, max_length=200)
    harvest_date: Optional[date] = None
    shelf_life_days: Optional[int] = Field(None, gt=0)
    storage_conditions: Optional[str] = Field(None, max_length=500)
    certifications: Optional[List[QualityCertification]] = None
    tags: Optional[List[str]] = None
    nutritional_info: Optional[Dict[str, Any]] = None
    is_featured: Optional[bool] = None
    is_seasonal: Optional[bool] = None
    season_start: Optional[int] = Field(None, ge=1, le=12)
    season_end: Optional[int] = Field(None, ge=1, le=12)
    status: Optional[ProductStatus] = None
    
    class Config:
        json_encoders = {
            Decimal: str,
            date: lambda v: v.isoformat() if v else None
        }


class ProductResponse(BaseModel):
    id: int
    name: str
    category: ProductCategory
    description: Optional[str]
    price: Decimal
    cost_price: Optional[Decimal]
    unit: ProductUnit
    stock_quantity: int
    min_stock_alert: int
    max_stock_limit: Optional[int]
    origin_location: Optional[str]
    harvest_date: Optional[date]
    shelf_life_days: Optional[int]
    storage_conditions: Optional[str]
    certifications: List[QualityCertification]
    tags: List[str]
    nutritional_info: Optional[Dict[str, Any]]
    status: ProductStatus
    is_featured: bool
    is_seasonal: bool
    season_start: Optional[int]
    season_end: Optional[int]
    merchant_id: int
    average_rating: float
    review_count: int
    sales_count: int
    images: List[str]
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    merchant: Optional[Dict[str, Any]] = None
    inventory_logs: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: str,
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }


class ProductListResponse(BaseModel):
    id: int
    name: str
    category: ProductCategory
    price: Decimal
    unit: ProductUnit
    stock_quantity: int
    status: ProductStatus
    is_featured: bool
    average_rating: float
    review_count: int
    sales_count: int
    main_image: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat() if v else None
        }


# 库存管理模型
class InventoryOperation(str, Enum):
    """库存操作类型"""
    IN = "in"                        # 入库
    OUT = "out"                      # 出库
    ADJUST = "adjust"                # 调整
    DAMAGED = "damaged"              # 损耗
    EXPIRED = "expired"              # 过期


class InventoryLogCreate(BaseModel):
    product_id: int = Field(..., description="产品ID")
    operation_type: InventoryOperation = Field(..., description="操作类型")
    quantity: int = Field(..., description="数量变化")
    unit_cost: Optional[Decimal] = Field(None, ge=0, description="单位成本")
    reason: Optional[str] = Field(None, max_length=500, description="变更原因")
    reference_no: Optional[str] = Field(None, max_length=100, description="参考单号")
    
    @validator('quantity')
    def validate_quantity(cls, v, values):
        if 'operation_type' in values:
            if values['operation_type'] in [InventoryOperation.OUT, InventoryOperation.DAMAGED, InventoryOperation.EXPIRED] and v > 0:
                return -v  # 出库操作自动转为负数
            elif values['operation_type'] == InventoryOperation.IN and v < 0:
                return abs(v)  # 入库操作自动转为正数
        return v
    
    class Config:
        json_encoders = {
            Decimal: str
        }


class InventoryLogResponse(BaseModel):
    id: int
    product_id: int
    operation_type: InventoryOperation
    quantity_change: int
    unit_cost: Optional[Decimal]
    total_cost: Optional[Decimal]
    stock_before: int
    stock_after: int
    reason: Optional[str]
    reference_no: Optional[str]
    operator_id: int
    created_at: datetime
    
    # 关联信息
    product: Optional[Dict[str, Any]] = None
    operator: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat() if v else None
        }


# 产品搜索筛选模型
class ProductSearchFilter(BaseModel):
    category: Optional[ProductCategory] = None
    status: Optional[ProductStatus] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    has_stock: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_seasonal: Optional[bool] = None
    certifications: Optional[List[QualityCertification]] = None
    origin_location: Optional[str] = None
    keyword: Optional[str] = Field(None, max_length=100, description="搜索关键词")
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方向")
    
    class Config:
        json_encoders = {
            Decimal: str
        }


# 产品统计模型
class ProductStatistics(BaseModel):
    total_products: int = Field(default=0, description="产品总数")
    active_products: int = Field(default=0, description="在售产品数")
    out_of_stock_products: int = Field(default=0, description="缺货产品数")
    low_stock_products: int = Field(default=0, description="低库存产品数")
    total_inventory_value: Decimal = Field(default=0, description="库存总价值")
    category_distribution: Dict[str, int] = Field(default_factory=dict, description="分类分布")
    sales_summary: Dict[str, Any] = Field(default_factory=dict, description="销售统计")
    recent_activities: List[Dict[str, Any]] = Field(default_factory=list, description="最近活动")
    
    class Config:
        json_encoders = {
            Decimal: str
        }


# 农产品组合销售模型
class ProductBundleCreate(BaseModel):
    service_id: int = Field(..., description="关联服务ID")
    product_ids: List[int] = Field(..., min_items=1, description="产品ID列表")
    bundle_price: Optional[Decimal] = Field(None, gt=0, description="组合价格")
    description: Optional[str] = Field(None, max_length=500, description="组合描述")
    
    class Config:
        json_encoders = {
            Decimal: str
        }


class ProductBundleResponse(BaseModel):
    id: int
    service_id: int
    bundle_price: Optional[Decimal]
    description: Optional[str]
    created_at: datetime
    
    # 关联信息
    service: Optional[Dict[str, Any]] = None
    products: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat() if v else None
        } 
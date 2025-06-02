from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Decimal, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class ProductStatus(enum.Enum):
    """产品状态枚举"""
    AVAILABLE = "available"  # 有库存
    OUT_OF_STOCK = "out_of_stock"  # 缺货
    DISCONTINUED = "discontinued"  # 停产
    SEASONAL = "seasonal"  # 季节性


class ProductCategory(enum.Enum):
    """产品分类枚举"""
    FRUITS = "fruits"  # 水果
    VEGETABLES = "vegetables"  # 蔬菜
    SEAFOOD = "seafood"  # 海鲜
    GRAINS = "grains"  # 谷物
    DAIRY = "dairy"  # 乳制品
    PROCESSED = "processed"  # 加工食品
    SPECIALTY = "specialty"  # 特产


class QualityGrade(enum.Enum):
    """质量等级枚举"""
    PREMIUM = "premium"  # 优质
    STANDARD = "standard"  # 标准
    BASIC = "basic"  # 基础


class AgriculturalProduct(Base):
    """农产品信息表"""
    __tablename__ = "agricultural_products"

    id = Column(Integer, primary_key=True, index=True, comment="产品ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="商家ID")
    
    # 基本信息
    name = Column(String(200), nullable=False, comment="产品名称")
    category = Column(Enum(ProductCategory), nullable=False, comment="产品分类")
    sku = Column(String(50), unique=True, comment="产品编码")
    barcode = Column(String(50), comment="条形码")
    
    # 详细信息
    description = Column(Text, comment="产品描述")
    origin_location = Column(String(100), comment="产地")
    harvest_season = Column(String(50), comment="收获季节")
    
    # 规格信息
    unit = Column(String(20), nullable=False, comment="销售单位（kg/箱/个等）")
    weight_per_unit = Column(Decimal(8, 3), comment="单位重量（kg）")
    package_size = Column(String(50), comment="包装规格")
    
    # 价格信息
    price = Column(Decimal(10, 2), nullable=False, comment="售价")
    cost_price = Column(Decimal(10, 2), comment="成本价")
    market_price = Column(Decimal(10, 2), comment="市场参考价")
    
    # 库存信息
    stock_quantity = Column(Integer, default=0, comment="库存数量")
    min_stock_alert = Column(Integer, default=10, comment="最低库存预警")
    max_stock_limit = Column(Integer, comment="最大库存限制")
    
    # 质量信息
    quality_grade = Column(Enum(QualityGrade), default=QualityGrade.STANDARD, comment="质量等级")
    certifications = Column(Text, comment="认证信息（JSON格式存储认证列表）")
    shelf_life_days = Column(Integer, comment="保质期（天）")
    storage_requirements = Column(Text, comment="储存要求")
    
    # 营养信息
    nutritional_info = Column(Text, comment="营养信息（JSON格式）")
    allergen_info = Column(Text, comment="过敏原信息")
    
    # 媒体资源
    images = Column(Text, comment="产品图片（JSON格式存储URL列表）")
    videos = Column(Text, comment="产品视频（JSON格式存储URL列表）")
    
    # 状态信息
    status = Column(Enum(ProductStatus), default=ProductStatus.AVAILABLE, comment="产品状态")
    is_featured = Column(Boolean, default=False, comment="是否推荐产品")
    is_organic = Column(Boolean, default=False, comment="是否有机产品")
    is_local = Column(Boolean, default=False, comment="是否本地产品")
    
    # 销售信息
    sales_count = Column(Integer, default=0, comment="销售数量")
    view_count = Column(Integer, default=0, comment="浏览次数")
    rating = Column(Decimal(3, 2), default=0.00, comment="产品评分")
    review_count = Column(Integer, default=0, comment="评价数量")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")
    last_restocked = Column(DateTime, comment="最后补货时间")
    
    # 关联关系
    merchant = relationship("Merchant", back_populates="agricultural_products")
    service_bundles = relationship("ServiceProductBundle", back_populates="product")
    inventory_logs = relationship("InventoryLog", back_populates="product")
    reviews = relationship("Review", back_populates="product")

    def __repr__(self):
        return f"<AgriculturalProduct(id={self.id}, name='{self.name}', category='{self.category}', status='{self.status}')>" 
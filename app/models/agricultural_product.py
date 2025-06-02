from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
from .enums import ProductCategory, ProductStatus


class AgriculturalProduct(Base):
    """农产品信息模型"""
    __tablename__ = "agricultural_products"

    id = Column(Integer, primary_key=True, index=True, comment="产品ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="所属商家ID")
    
    # 基本信息
    name = Column(String(100), nullable=False, comment="产品名称")
    category = Column(SQLEnum(ProductCategory), nullable=False, comment="产品类别")
    variety = Column(String(50), comment="品种")
    brand = Column(String(50), comment="品牌")
    description = Column(Text, comment="产品描述")
    
    # 产地信息
    origin = Column(String(100), comment="产地")
    farm_name = Column(String(100), comment="农场名称")
    growing_method = Column(String(50), comment="种植方式（有机、绿色等）")
    harvest_season = Column(String(50), comment="收获季节")
    
    # 价格信息
    unit_price = Column(Numeric(8, 2), nullable=False, comment="单价")
    unit = Column(String(20), nullable=False, comment="单位（kg、个、箱等）")
    wholesale_price = Column(Numeric(8, 2), comment="批发价")
    min_order_quantity = Column(Integer, default=1, comment="最小起订量")
    
    # 库存信息
    stock_quantity = Column(Integer, default=0, comment="库存数量")
    available_quantity = Column(Integer, default=0, comment="可售数量")
    reserved_quantity = Column(Integer, default=0, comment="预留数量")
    reorder_level = Column(Integer, default=10, comment="补货水平")
    
    # 产品规格
    weight_per_unit = Column(Numeric(8, 3), comment="单位重量(kg)")
    size_specification = Column(String(100), comment="尺寸规格")
    package_type = Column(String(50), comment="包装类型")
    shelf_life = Column(Integer, comment="保质期(天)")
    
    # 营养信息
    nutritional_info = Column(Text, comment="营养成分，JSON格式")
    calories_per_100g = Column(Numeric(6, 2), comment="每100g热量")
    storage_conditions = Column(String(255), comment="储存条件")
    
    # 质量认证
    certifications = Column(Text, comment="质量认证，JSON格式")
    quality_grade = Column(String(20), comment="质量等级")
    safety_standards = Column(Text, comment="安全标准")
    
    # 媒体信息
    cover_image = Column(String(255), comment="封面图片URL")
    gallery_images = Column(Text, comment="产品图片URLs，JSON格式")
    video_url = Column(String(255), comment="产品视频URL")
    
    # 销售信息
    total_sales = Column(Integer, default=0, comment="总销量")
    rating = Column(Numeric(3, 2), default=0.00, comment="平均评分")
    total_reviews = Column(Integer, default=0, comment="总评价数")
    
    # 配送信息
    shipping_required = Column(Boolean, default=True, comment="是否需要配送")
    shipping_cost = Column(Numeric(6, 2), comment="配送费用")
    delivery_time = Column(String(50), comment="配送时间")
    pickup_available = Column(Boolean, default=False, comment="是否支持自提")
    
    # 促销信息
    is_on_sale = Column(Boolean, default=False, comment="是否促销")
    sale_price = Column(Numeric(8, 2), comment="促销价格")
    sale_start_date = Column(DateTime, comment="促销开始时间")
    sale_end_date = Column(DateTime, comment="促销结束时间")
    
    # 状态信息
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.AVAILABLE, comment="产品状态")
    is_featured = Column(Boolean, default=False, comment="是否推荐")
    sort_order = Column(Integer, default=0, comment="排序")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    merchant = relationship("Merchant", back_populates="agricultural_products")
    order_items = relationship("OrderItem", back_populates="product")
    inventory_logs = relationship("InventoryLog", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    
    def __repr__(self):
        return f"<AgriculturalProduct(id={self.id}, name='{self.name}', category='{self.category}', price={self.unit_price})>" 
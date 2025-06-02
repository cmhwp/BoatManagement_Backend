from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class AgriculturalProduct(Base):
    """农产品信息模型"""
    __tablename__ = "agricultural_products"

    id = Column(Integer, primary_key=True, index=True, comment="产品ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="提供商家ID")
    
    # 基础信息
    name = Column(String(100), nullable=False, comment="产品名称")
    category = Column(String(50), nullable=False, comment="产品分类")
    variety = Column(String(50), comment="品种")
    origin = Column(String(100), comment="产地")
    
    # 产品详情
    description = Column(Text, comment="产品描述")
    specifications = Column(String(200), comment="规格")
    unit = Column(String(20), comment="销售单位")
    
    # 价格库存
    price = Column(Numeric(10, 2), nullable=False, comment="单价")
    stock_quantity = Column(Integer, default=0, comment="库存数量")
    min_order_quantity = Column(Integer, default=1, comment="最小起订量")
    
    # 质量信息
    quality_grade = Column(String(20), comment="质量等级")
    organic_certified = Column(Boolean, default=False, comment="是否有机认证")
    certification_no = Column(String(50), comment="认证编号")
    
    # 时间信息
    harvest_date = Column(DateTime, comment="收获时间")
    shelf_life = Column(Integer, comment="保质期(天)")
    storage_requirements = Column(Text, comment="储存要求")
    
    # 销售信息
    is_available = Column(Boolean, default=True, comment="是否可售")
    is_seasonal = Column(Boolean, default=False, comment="是否季节性产品")
    season_start = Column(DateTime, comment="销售季节开始")
    season_end = Column(DateTime, comment="销售季节结束")
    
    # 营养信息
    nutrition_info = Column(Text, comment="营养成分(JSON格式)")
    calories_per_100g = Column(Numeric(8, 2), comment="每100g热量")
    
    # 评价信息
    rating = Column(Numeric(3, 2), default=0.0, comment="产品评分")
    total_sold = Column(Integer, default=0, comment="总销售量")
    
    # 媒体信息
    images = Column(Text, comment="产品图片URLs(JSON格式)")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    merchant = relationship("Merchant")
    
    def __repr__(self):
        return f"<AgriculturalProduct(id={self.id}, name='{self.name}', category='{self.category}')>" 
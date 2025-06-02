from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.config.database import Base


class SystemConfig(Base):
    """系统参数配置模型"""
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True, comment="配置ID")
    
    # 配置信息
    config_key = Column(String(100), unique=True, nullable=False, comment="配置键")
    config_value = Column(Text, comment="配置值")
    config_type = Column(String(20), default="string", comment="配置类型（string/int/float/bool/json）")
    
    # 分组信息
    category = Column(String(50), comment="配置分类")
    subcategory = Column(String(50), comment="配置子分类")
    
    # 描述信息
    display_name = Column(String(100), comment="显示名称")
    description = Column(Text, comment="配置描述")
    default_value = Column(Text, comment="默认值")
    
    # 约束信息
    is_editable = Column(Boolean, default=True, comment="是否可编辑")
    is_public = Column(Boolean, default=False, comment="是否公开")
    validation_rule = Column(Text, comment="验证规则")
    
    # 排序信息
    sort_order = Column(Integer, default=0, comment="排序顺序")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<SystemConfig(id={self.id}, key='{self.config_key}', value='{self.config_value}')>" 
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from datetime import datetime
import enum
from app.db.database import Base


class ConfigType(enum.Enum):
    """配置类型枚举"""
    SYSTEM = "system"  # 系统配置
    PAYMENT = "payment"  # 支付配置
    NOTIFICATION = "notification"  # 通知配置
    SHIPPING = "shipping"  # 物流配置
    BUSINESS = "business"  # 业务配置
    SECURITY = "security"  # 安全配置


class DataType(enum.Enum):
    """数据类型枚举"""
    STRING = "string"  # 字符串
    INTEGER = "integer"  # 整数
    FLOAT = "float"  # 浮点数
    BOOLEAN = "boolean"  # 布尔值
    JSON = "json"  # JSON对象
    TEXT = "text"  # 文本


class SystemConfig(Base):
    """系统参数配置表"""
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True, comment="配置ID")
    
    # 基本信息
    key = Column(String(100), unique=True, nullable=False, comment="配置键名")
    name = Column(String(200), nullable=False, comment="配置名称")
    description = Column(Text, comment="配置描述")
    
    # 配置分类
    config_type = Column(Enum(ConfigType), nullable=False, comment="配置类型")
    group_name = Column(String(100), comment="配置分组")
    
    # 配置值
    value = Column(Text, comment="配置值")
    default_value = Column(Text, comment="默认值")
    data_type = Column(Enum(DataType), default=DataType.STRING, comment="数据类型")
    
    # 验证规则
    validation_rule = Column(Text, comment="验证规则（JSON格式）")
    options = Column(Text, comment="可选值列表（JSON格式，用于枚举类型）")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_readonly = Column(Boolean, default=False, comment="是否只读")
    is_sensitive = Column(Boolean, default=False, comment="是否敏感信息")
    
    # 排序和显示
    sort_order = Column(Integer, default=0, comment="排序顺序")
    is_visible = Column(Boolean, default=True, comment="是否在界面显示")
    
    # 变更记录
    last_modified_by = Column(Integer, comment="最后修改人ID")
    modification_reason = Column(Text, comment="修改原因")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")

    def __repr__(self):
        return f"<SystemConfig(id={self.id}, key='{self.key}', type='{self.config_type}')>" 
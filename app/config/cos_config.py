from pydantic_settings import BaseSettings
from typing import Optional


class COSSettings(BaseSettings):
    """腾讯云COS配置"""
    
    # COS 基本配置
    cos_secret_id: str
    cos_secret_key: str
    cos_region: str = "ap-guangzhou"
    cos_bucket: str
    
    # COS 域名配置
    cos_domain: str
    
    # 上传配置
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_types: list = ["jpg", "jpeg", "png", "gif", "webp"]
    
    # 文件路径配置
    avatar_prefix: str = "avatars/"
    identity_prefix: str = "identity/"
    boat_prefix: str = "boats/"
    service_prefix: str = "services/"
    product_prefix: str = "products/"
    review_prefix: str = "reviews/"
    
    class Config:
        env_file = ".env"
        env_prefix = "COS_"
        extra = "ignore"  # 忽略额外的字段


# 创建全局COS配置实例
cos_settings = COSSettings() 
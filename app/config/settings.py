from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """应用配置设置"""
    
    # 数据库配置
    database_url: str = "mysql+pymysql://root:123456@localhost:3306/boat_management_db"
    
    # JWT配置
    secret_key: str = "your-secret-key-here-please-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 3600
    
    # 应用配置
    app_name: str = "绿色智能船艇农文旅平台"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # CORS配置
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建全局设置实例
settings = Settings() 
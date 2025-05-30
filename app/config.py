from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "mysql+pymysql://username:password@localhost:3306/boat_management_db"
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "username"
    db_password: str = "password"
    db_name: str = "boat_management_db"
    
    # JWT配置
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # 应用配置
    app_name: str = "绿色智能船艇农文旅服务平台"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # 文件上传配置
    upload_path: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings() 
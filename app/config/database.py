from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import settings

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # 在调试模式下打印SQL语句
    pool_pre_ping=True,   # 连接池预ping
    pool_recycle=3600,    # 连接回收时间
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """获取数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
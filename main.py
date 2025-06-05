from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.database import engine, Base
from app.models import *  # 导入所有模型以便创建表
from app.routers import auth, users, merchants, crews, boats, admin, identity_verification

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于FastAPI的绿色智能船艇农文旅平台后端API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)  # 认证路由
app.include_router(users.router)  # 用户路由
app.include_router(merchants.router)  # 商家路由
app.include_router(crews.router)  # 船员路由
app.include_router(boats.router)  # 船艇路由
app.include_router(admin.router)  # 管理员路由
app.include_router(identity_verification.router)  # 实名认证路由


@app.get("/", tags=["根路径"])
async def root():
    """根路径欢迎信息"""
    return {
        "message": "欢迎使用绿色智能船艇农文旅平台API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "features": [
            "用户认证与授权",
            "实名认证管理",
            "商家管理",
            "船员管理", 
            "船艇管理",
            "管理员功能"
        ]
    }


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": settings.app_name}


@app.get("/api/info", tags=["系统"])
async def api_info():
    """API信息接口"""
    return {
        "api_version": "v1",
        "service": settings.app_name,
        "environment": "development" if settings.debug else "production",
        "available_endpoints": {
            "auth": "/api/v1/auth - 用户认证",
            "users": "/api/v1/users - 用户管理",
            "identity_verification": "/api/v1/identity-verification - 实名认证",
            "merchants": "/api/v1/merchants - 商家管理",
            "crews": "/api/v1/crews - 船员管理",
            "boats": "/api/v1/boats - 船艇管理",
            "admin": "/api/v1/admin - 管理员功能"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

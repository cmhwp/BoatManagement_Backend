from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.requests import Request
import uvicorn
from app.config import get_settings
from app.db.database import engine, Base
from app.routers import (
    auth_router,
    users_router,
    merchants_router,
    boats_router,
    services_router,
    orders_router,
    products_router
)

settings = get_settings()

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于绿色智能船艇的农文旅服务平台后端API",
    debug=settings.debug
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "message": "服务器内部错误",
            "status_code": 500
        }
    )

# 注册路由
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(merchants_router)
app.include_router(boats_router)
app.include_router(services_router)
app.include_router(orders_router)
app.include_router(products_router)

@app.get("/", summary="根路径")
def read_root():
    """根路径，返回API信息"""
    return {
        "message": f"欢迎使用{settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", summary="健康检查")
def health_check():
    """健康检查接口"""
    return {"status": "healthy", "message": "服务正常运行"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 
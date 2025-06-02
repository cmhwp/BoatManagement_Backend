from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import os
from contextlib import asynccontextmanager

from app.db.database import create_tables
from app.routers import auth, users, merchants, boats, services, products, orders, reviews, payments, notifications
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序生命周期管理"""
    # 启动时执行
    logger.info("🚀 启动绿色智能船艇农文旅服务平台后端服务")
    
    # 创建数据库表
    try:
        create_tables()
        logger.info("✅ 数据库表创建成功")
    except Exception as e:
        logger.error(f"❌ 数据库表创建失败: {e}")
    
    yield
    
    # 关闭时执行
    logger.info("🔄 关闭服务")


# 创建FastAPI应用实例
app = FastAPI(
    title="绿色智能船艇农文旅服务平台",
    description="基于FastAPI的绿色智能船艇农文旅服务平台后端API系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 可信主机中间件（生产环境使用）
if os.getenv("ENV") == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["example.com", "*.example.com"]
    )


# 请求计时中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # 记录慢请求
    if process_time > 1.0:
        logger.warning(f"慢请求: {request.method} {request.url} - {process_time:.2f}s")
    
    return response


# 全局异常处理
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None,
            "error_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理"""
    logger.error(f"请求验证错误: {exc.errors()} - {request.url}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "请求参数验证失败",
            "data": None,
            "errors": exc.errors(),
            "error_code": 422
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"服务器内部错误: {str(exc)} - {request.url}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "服务器内部错误",
            "data": None,
            "error_code": 500
        }
    )


# 根路径
@app.get("/")
async def root():
    """API根路径"""
    return {
        "success": True,
        "message": "欢迎使用绿色智能船艇农文旅服务平台API",
        "data": {
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "success": True,
        "message": "服务正常运行",
        "data": {
            "status": "healthy",
            "timestamp": time.time()
        }
    }


# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(merchants.router, prefix="/api/v1/merchants", tags=["商家"])
app.include_router(boats.router, prefix="/api/v1/boats", tags=["船艇"])
app.include_router(services.router, prefix="/api/v1/services", tags=["服务"])
app.include_router(products.router, prefix="/api/v1/products", tags=["农产品"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["订单"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["评价"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["支付"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["通知"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENV") == "development" else False,
        log_level="info"
    )

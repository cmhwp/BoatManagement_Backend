from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse


def create_response(
    success: bool = True,
    message: str = "操作成功",
    data: Any = None,
    error_code: Optional[int] = None,
    status_code: int = 200
) -> JSONResponse:
    """创建统一格式的响应"""
    response_data = {
        "success": success,
        "message": message,
        "data": data
    }
    
    if error_code is not None:
        response_data["error_code"] = error_code
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


def success_response(
    message: str = "操作成功",
    data: Any = None,
    status_code: int = 200
) -> JSONResponse:
    """成功响应"""
    return create_response(
        success=True,
        message=message,
        data=data,
        status_code=status_code
    )


def error_response(
    message: str = "操作失败",
    error_code: Optional[int] = None,
    status_code: int = 400
) -> JSONResponse:
    """错误响应"""
    return create_response(
        success=False,
        message=message,
        data=None,
        error_code=error_code,
        status_code=status_code
    )


def paginated_response(
    data: list,
    total: int,
    page: int,
    size: int,
    message: str = "获取数据成功"
) -> JSONResponse:
    """分页响应"""
    return success_response(
        message=message,
        data={
            "items": data,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    ) 
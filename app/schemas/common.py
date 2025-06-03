from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')


class PaginationParams(BaseModel):
    """分页参数模式"""
    page: int = 1
    page_size: int = 20
    
    def get_offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    def get_limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模式"""
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )


class ApiResponse(BaseModel, Generic[T]):
    """API响应模式"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[T] = None
    
    @classmethod
    def success_response(cls, data: T = None, message: str = "操作成功"):
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def error_response(cls, message: str = "操作失败"):
        return cls(success=False, message=message, data=None)


class IdResponse(BaseModel):
    """ID响应模式"""
    id: int
    
    
class MessageResponse(BaseModel):
    """消息响应模式"""
    message: str 
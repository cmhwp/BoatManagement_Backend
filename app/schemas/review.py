from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime


class ReviewBase(BaseModel):
    """评价基础模型"""
    rating: int
    title: Optional[str] = None
    content: Optional[str] = None
    service_rating: Optional[int] = None
    quality_rating: Optional[int] = None
    value_rating: Optional[int] = None
    is_anonymous: bool = False
    
    @field_validator('rating', 'service_rating', 'quality_rating', 'value_rating')
    @classmethod
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('评分必须在1-5之间')
        return v


class ReviewCreate(ReviewBase):
    """评价创建模型"""
    order_id: int
    service_id: Optional[int] = None
    product_id: Optional[int] = None
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    
    @field_validator('order_id')
    @classmethod
    def validate_order_id(cls, v):
        if v <= 0:
            raise ValueError('订单ID必须大于0')
        return v


class ReviewUpdate(BaseModel):
    """评价更新模型"""
    rating: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    service_rating: Optional[int] = None
    quality_rating: Optional[int] = None
    value_rating: Optional[int] = None
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    is_anonymous: Optional[bool] = None
    
    @field_validator('rating', 'service_rating', 'quality_rating', 'value_rating')
    @classmethod
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('评分必须在1-5之间')
        return v


class ReviewResponse(BaseModel):
    """评价响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    order_id: Optional[int] = None
    service_id: Optional[int] = None
    product_id: Optional[int] = None
    rating: int
    title: Optional[str] = None
    content: Optional[str] = None
    service_rating: Optional[int] = None
    quality_rating: Optional[int] = None
    value_rating: Optional[int] = None
    images: Optional[str] = None  # JSON string
    videos: Optional[str] = None  # JSON string
    is_anonymous: bool
    is_verified_purchase: bool
    is_hidden: bool
    admin_notes: Optional[str] = None
    helpful_count: int
    reply_count: int
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    service_title: Optional[str] = None
    product_name: Optional[str] = None


class ReviewListResponse(BaseModel):
    """评价列表响应模型"""
    id: int
    user_id: int
    rating: int
    title: Optional[str] = None
    content: Optional[str] = None
    is_anonymous: bool
    is_verified_purchase: bool
    helpful_count: int
    reply_count: int
    created_at: datetime
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None


class ReviewReply(BaseModel):
    """评价回复模型"""
    content: str
    is_merchant: bool = False
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('回复内容不能为空')
        if len(v) > 500:
            raise ValueError('回复内容不能超过500字符')
        return v


class ReviewReplyResponse(BaseModel):
    """评价回复响应模型"""
    id: int
    review_id: int
    user_id: int
    content: str
    is_merchant: bool
    created_at: datetime
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None


class ReviewStatistics(BaseModel):
    """评价统计模型"""
    total_reviews: int
    average_rating: float
    rating_distribution: dict  # {1: count, 2: count, ...}
    recent_reviews: int
    response_rate: float  # 商家回复率


class ReviewSearchFilter(BaseModel):
    """评价搜索筛选模型"""
    service_id: Optional[int] = None
    product_id: Optional[int] = None
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    has_content: Optional[bool] = None
    has_images: Optional[bool] = None
    is_verified: Optional[bool] = None
    keyword: Optional[str] = None


class ReviewHelpful(BaseModel):
    """评价有用性操作模型"""
    is_helpful: bool


class ReviewModerationAction(BaseModel):
    """评价审核操作模型"""
    action: str  # hide, show, delete
    admin_notes: Optional[str] = None
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        allowed_actions = ['hide', 'show', 'delete']
        if v not in allowed_actions:
            raise ValueError(f'操作必须是以下之一: {", ".join(allowed_actions)}')
        return v 
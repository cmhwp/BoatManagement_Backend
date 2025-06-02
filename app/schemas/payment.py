from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum


class PaymentMethod(str, Enum):
    """支付方式枚举"""
    WECHAT_PAY = "wechat_pay"      # 微信支付
    ALIPAY = "alipay"              # 支付宝
    BANK_CARD = "bank_card"        # 银行卡
    BALANCE = "balance"            # 余额支付
    CREDIT_CARD = "credit_card"    # 信用卡


class PaymentStatus(str, Enum):
    """支付状态枚举"""
    PENDING = "pending"            # 待支付
    PROCESSING = "processing"      # 支付中
    SUCCESS = "success"            # 支付成功
    FAILED = "failed"              # 支付失败
    CANCELLED = "cancelled"        # 已取消
    REFUNDING = "refunding"        # 退款中
    REFUNDED = "refunded"          # 已退款
    PARTIAL_REFUNDED = "partial_refunded"  # 部分退款


class RefundStatus(str, Enum):
    """退款状态枚举"""
    PENDING = "pending"            # 待处理
    PROCESSING = "processing"      # 处理中
    SUCCESS = "success"            # 退款成功
    FAILED = "failed"              # 退款失败
    REJECTED = "rejected"          # 已拒绝


# 支付创建模型
class PaymentCreate(BaseModel):
    order_id: int = Field(..., description="订单ID")
    payment_method: PaymentMethod = Field(..., description="支付方式")
    return_url: Optional[str] = Field(None, description="支付成功返回URL")
    notify_url: Optional[str] = Field(None, description="支付通知回调URL")
    description: Optional[str] = Field(None, max_length=200, description="支付描述")
    
    class Config:
        json_encoders = {
            Decimal: str
        }


class PaymentUpdate(BaseModel):
    payment_method: Optional[PaymentMethod] = None
    description: Optional[str] = Field(None, max_length=200)
    
    class Config:
        json_encoders = {
            Decimal: str
        }


class PaymentResponse(BaseModel):
    id: int
    payment_no: str
    order_id: int
    user_id: int
    amount: Decimal
    payment_method: PaymentMethod
    status: PaymentStatus
    transaction_id: Optional[str]
    third_party_transaction_id: Optional[str]
    description: Optional[str]
    payment_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    order: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None
    refunds: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat() if v else None
        }


class PaymentListResponse(BaseModel):
    id: int
    payment_no: str
    order_id: int
    amount: Decimal
    payment_method: PaymentMethod
    status: PaymentStatus
    payment_time: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat() if v else None
        }


# 退款相关模型
class RefundCreate(BaseModel):
    payment_id: int = Field(..., description="支付记录ID")
    refund_amount: Decimal = Field(..., gt=0, description="退款金额")
    reason: str = Field(..., min_length=1, max_length=500, description="退款原因")
    
    @validator('refund_amount')
    def validate_refund_amount(cls, v):
        if v <= 0:
            raise ValueError('退款金额必须大于0')
        return v
    
    class Config:
        json_encoders = {
            Decimal: str
        }


class RefundUpdate(BaseModel):
    status: RefundStatus
    reject_reason: Optional[str] = Field(None, max_length=500, description="拒绝原因")
    
    class Config:
        json_encoders = {
            Decimal: str
        }


class RefundResponse(BaseModel):
    id: int
    refund_no: str
    payment_id: int
    refund_amount: Decimal
    status: RefundStatus
    reason: str
    reject_reason: Optional[str]
    refund_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    payment: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat() if v else None
        }


# 支付回调模型
class PaymentCallback(BaseModel):
    payment_no: str = Field(..., description="支付单号")
    status: PaymentStatus = Field(..., description="支付状态")
    third_party_transaction_id: Optional[str] = Field(None, description="第三方交易号")
    amount: Optional[Decimal] = Field(None, description="实际支付金额")
    callback_data: Optional[Dict[str, Any]] = Field(None, description="回调原始数据")
    
    class Config:
        json_encoders = {
            Decimal: str
        }


# 支付统计模型
class PaymentStatistics(BaseModel):
    total_amount: Decimal = Field(default=0, description="总支付金额")
    total_count: int = Field(default=0, description="总支付次数")
    success_amount: Decimal = Field(default=0, description="成功支付金额")
    success_count: int = Field(default=0, description="成功支付次数")
    success_rate: float = Field(default=0.0, description="支付成功率")
    refund_amount: Decimal = Field(default=0, description="退款金额")
    refund_count: int = Field(default=0, description="退款次数")
    method_distribution: Dict[str, int] = Field(default_factory=dict, description="支付方式分布")
    daily_amounts: List[Dict[str, Any]] = Field(default_factory=list, description="每日支付金额")
    
    class Config:
        json_encoders = {
            Decimal: str
        }


# 支付搜索筛选模型
class PaymentSearchFilter(BaseModel):
    order_id: Optional[int] = None
    payment_method: Optional[PaymentMethod] = None
    status: Optional[PaymentStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    keyword: Optional[str] = Field(None, max_length=100, description="搜索关键词")
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat() if v else None
        }


# 支付链接响应模型
class PaymentLinkResponse(BaseModel):
    payment_id: int
    payment_no: str
    payment_url: str
    qr_code_url: Optional[str] = None
    expires_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        } 
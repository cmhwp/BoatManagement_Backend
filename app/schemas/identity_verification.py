from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from app.models.enums import IdentityType, VerificationStatus


class IdentityVerificationCreate(BaseModel):
    """创建实名认证请求模式"""
    real_name: str = Field(..., max_length=50, description="真实姓名")
    identity_type: IdentityType = Field(default=IdentityType.ID_CARD, description="证件类型")
    identity_number: str = Field(..., max_length=30, description="证件号码")
    front_image: Optional[str] = Field(None, description="证件正面照片URL")
    back_image: Optional[str] = Field(None, description="证件背面照片URL")

    @field_validator('identity_number')
    @classmethod
    def validate_identity_number(cls, v: str, info: ValidationInfo):
        """验证证件号码格式"""
        if not v or not v.strip():
            raise ValueError("证件号码不能为空")
        
        # 从 info.data 获取其他字段的值
        identity_type = info.data.get('identity_type') if info.data else None
        if identity_type == IdentityType.ID_CARD:
            # 简单的身份证号码验证
            if len(v) not in [15, 18]:
                raise ValueError("身份证号码长度不正确")
        elif identity_type == IdentityType.PASSPORT:
            # 护照号码验证
            if len(v) < 6 or len(v) > 20:
                raise ValueError("护照号码长度不正确")
        
        return v.strip()

    @field_validator('real_name')
    @classmethod
    def validate_real_name(cls, v: str):
        """验证真实姓名"""
        if not v or not v.strip():
            raise ValueError("真实姓名不能为空")
        return v.strip()


class IdentityVerificationUpdate(BaseModel):
    """更新实名认证请求模式"""
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    identity_type: Optional[IdentityType] = Field(None, description="证件类型")
    identity_number: Optional[str] = Field(None, max_length=30, description="证件号码")
    front_image: Optional[str] = Field(None, description="证件正面照片URL")
    back_image: Optional[str] = Field(None, description="证件背面照片URL")


class IdentityVerificationReview(BaseModel):
    """审核实名认证请求模式"""
    status: VerificationStatus = Field(..., description="审核状态")
    reject_reason: Optional[str] = Field(None, description="拒绝原因")
    expires_at: Optional[datetime] = Field(None, description="认证过期时间")

    @field_validator('reject_reason')
    @classmethod
    def validate_reject_reason(cls, v: Optional[str], info: ValidationInfo):
        """验证拒绝原因"""
        # 从 info.data 获取其他字段的值
        status = info.data.get('status') if info.data else None
        if status == VerificationStatus.REJECTED and not v:
            raise ValueError("拒绝时必须提供拒绝原因")
        return v


class IdentityVerificationResponse(BaseModel):
    """实名认证响应模式"""
    id: int
    user_id: int
    real_name: str
    identity_type: IdentityType
    identity_number: str
    front_image: Optional[str] = None
    back_image: Optional[str] = None
    status: VerificationStatus
    reject_reason: Optional[str] = None
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    reviewer_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IdentityVerificationSummary(BaseModel):
    """实名认证摘要模式（用于列表展示）"""
    id: int
    user_id: int
    real_name: str
    identity_type: IdentityType
    status: VerificationStatus
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True 
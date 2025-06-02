from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Review(Base):
    """用户评价数据模型"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True, comment="评价ID")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="关联订单ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="评价用户ID")
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, comment="被评价商家ID")
    
    # 评分信息
    overall_rating = Column(Numeric(3, 2), nullable=False, comment="总体评分(1-5)")
    service_rating = Column(Numeric(3, 2), comment="服务评分")
    quality_rating = Column(Numeric(3, 2), comment="质量评分")
    value_rating = Column(Numeric(3, 2), comment="性价比评分")
    
    # 评价内容
    title = Column(String(100), comment="评价标题")
    content = Column(Text, comment="评价内容")
    images = Column(Text, comment="评价图片URLs(JSON格式)")
    
    # 状态信息
    is_anonymous = Column(Boolean, default=False, comment="是否匿名")
    is_visible = Column(Boolean, default=True, comment="是否可见")
    
    # 商家回复
    merchant_reply = Column(Text, comment="商家回复")
    replied_at = Column(DateTime, comment="回复时间")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="评价时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    order = relationship("Order", back_populates="reviews")
    user = relationship("User")
    merchant = relationship("Merchant")
    
    def __repr__(self):
        return f"<Review(id={self.id}, order_id={self.order_id}, rating={self.overall_rating})>" 
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Review(Base):
    """用户评价数据表"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True, comment="评价ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    order_id = Column(Integer, ForeignKey("orders.id"), comment="订单ID")
    
    # 评价对象
    service_id = Column(Integer, ForeignKey("services.id"), comment="服务ID")
    product_id = Column(Integer, ForeignKey("agricultural_products.id"), comment="产品ID")
    
    # 评价内容
    rating = Column(Integer, nullable=False, comment="评分（1-5星）")
    title = Column(String(200), comment="评价标题")
    content = Column(Text, comment="评价内容")
    
    # 详细评分
    service_rating = Column(Integer, comment="服务评分")
    quality_rating = Column(Integer, comment="质量评分")
    value_rating = Column(Integer, comment="性价比评分")
    
    # 媒体资源
    images = Column(Text, comment="评价图片（JSON格式存储URL列表）")
    videos = Column(Text, comment="评价视频（JSON格式存储URL列表）")
    
    # 状态信息
    is_anonymous = Column(Boolean, default=False, comment="是否匿名评价")
    is_verified_purchase = Column(Boolean, default=True, comment="是否验证购买")
    
    # 管理信息
    is_hidden = Column(Boolean, default=False, comment="是否隐藏")
    admin_notes = Column(Text, comment="管理员备注")
    
    # 统计信息
    helpful_count = Column(Integer, default=0, comment="有用数")
    reply_count = Column(Integer, default=0, comment="回复数")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="评价时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="reviews")
    order = relationship("Order", back_populates="reviews")
    service = relationship("Service", back_populates="reviews")
    product = relationship("AgriculturalProduct", back_populates="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, rating={self.rating})>" 
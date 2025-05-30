from sqlalchemy import Column, Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class ServiceProductBundle(Base):
    __tablename__ = "service_product_bundles"

    bundle_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("services.service_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("agricultural_products.product_id"), nullable=False)
    discount_rate = Column(DECIMAL(5, 2), default=0.00)  # 折扣率

    # 关系
    service = relationship("Service", back_populates="product_bundles")
    product = relationship("AgriculturalProduct", back_populates="product_bundles") 
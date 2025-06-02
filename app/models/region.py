from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Region(Base):
    """地区信息表"""
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True, comment="地区ID")
    name = Column(String(100), nullable=False, comment="地区名称")
    code = Column(String(20), unique=True, index=True, comment="地区编码")
    parent_id = Column(Integer, ForeignKey("regions.id"), comment="父级地区ID")
    level = Column(Integer, default=1, comment="地区级别（1:省/直辖市，2:市，3:区县）")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    
    # 自关联关系
    parent = relationship("Region", remote_side=[id], back_populates="children")
    children = relationship("Region", back_populates="parent")
    
    # 关联关系
    users = relationship("User", back_populates="region")
    merchants = relationship("Merchant", back_populates="region")
    services = relationship("Service", back_populates="region")

    def __repr__(self):
        return f"<Region(id={self.id}, name='{self.name}', code='{self.code}', level={self.level})>" 
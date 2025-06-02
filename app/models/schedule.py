from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Schedule(Base):
    """船员船艇排班模型"""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True, comment="排班ID")
    boat_id = Column(Integer, ForeignKey("boats.id"), nullable=False, comment="船艇ID")
    crew_id = Column(Integer, ForeignKey("crew_info.id"), nullable=False, comment="船员ID")
    service_id = Column(Integer, ForeignKey("services.id"), comment="关联服务ID")
    
    # 排班时间
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")
    
    # 排班信息
    shift_type = Column(String(20), comment="班次类型")
    status = Column(String(20), default="scheduled", comment="排班状态")
    
    # 路线信息
    route = Column(Text, comment="航行路线")
    departure_point = Column(String(200), comment="出发地点")
    destination = Column(String(200), comment="目的地")
    
    # 备注
    notes = Column(Text, comment="备注信息")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    boat = relationship("Boat", back_populates="schedules")
    crew = relationship("CrewInfo", back_populates="schedules")
    service = relationship("Service")
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, boat_id={self.boat_id}, crew_id={self.crew_id}, status='{self.status}')>" 
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class ScheduleStatus(enum.Enum):
    """排班状态枚举"""
    SCHEDULED = "scheduled"  # 已排班
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class Schedule(Base):
    """船员船艇排班表"""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True, comment="排班ID")
    boat_id = Column(Integer, ForeignKey("boats.id"), nullable=False, comment="船艇ID")
    crew_id = Column(Integer, ForeignKey("crew_info.id"), nullable=False, comment="船员ID")
    service_id = Column(Integer, ForeignKey("services.id"), comment="关联服务ID")
    
    # 排班时间
    start_datetime = Column(DateTime, nullable=False, comment="开始时间")
    end_datetime = Column(DateTime, nullable=False, comment="结束时间")
    
    # 排班信息
    role = Column(String(50), comment="船员角色（船长/副手/服务员等）")
    duties = Column(Text, comment="工作职责（JSON格式）")
    
    # 状态信息
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.SCHEDULED, comment="排班状态")
    
    # 备注信息
    notes = Column(Text, comment="排班备注")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")
    
    # 关联关系
    boat = relationship("Boat", back_populates="schedules")
    crew = relationship("CrewInfo", back_populates="schedules")
    service = relationship("Service", back_populates="schedules")

    def __repr__(self):
        return f"<Schedule(id={self.id}, boat_id={self.boat_id}, crew_id={self.crew_id}, status='{self.status}')>" 
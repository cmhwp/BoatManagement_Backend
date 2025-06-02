from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class Schedule(Base):
    """船员船艇排班模型"""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True, comment="排班ID")
    crew_id = Column(Integer, ForeignKey("crew_info.id"), nullable=False, comment="船员ID")
    boat_id = Column(Integer, ForeignKey("boats.id"), nullable=False, comment="船艇ID")
    order_id = Column(Integer, ForeignKey("orders.id"), comment="关联订单ID")
    
    # 排班信息
    schedule_date = Column(DateTime, nullable=False, comment="排班日期")
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")
    shift_type = Column(String(20), comment="班次类型（上午/下午/全天）")
    
    # 任务信息
    task_description = Column(Text, comment="任务描述")
    route_plan = Column(Text, comment="航行计划，JSON格式")
    passenger_count = Column(Integer, comment="预计载客数")
    
    # 状态信息
    is_confirmed = Column(Boolean, default=False, comment="是否已确认")
    is_completed = Column(Boolean, default=False, comment="是否已完成")
    is_cancelled = Column(Boolean, default=False, comment="是否已取消")
    
    # 实际执行信息
    actual_start_time = Column(DateTime, comment="实际开始时间")
    actual_end_time = Column(DateTime, comment="实际结束时间")
    actual_passenger_count = Column(Integer, comment="实际载客数")
    
    # 备注信息
    notes = Column(Text, comment="排班备注")
    completion_notes = Column(Text, comment="完成备注")
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    crew = relationship("CrewInfo", back_populates="schedules")
    boat = relationship("Boat", back_populates="schedules")
    order = relationship("Order")
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, crew_id={self.crew_id}, boat_id={self.boat_id}, date={self.schedule_date})>" 
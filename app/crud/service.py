from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.service import Service
from app.models.enums import ServiceStatus


def get_service_by_id(db: Session, service_id: int) -> Optional[Service]:
    """根据ID获取服务"""
    return db.query(Service).filter(Service.id == service_id).first()


def get_services_by_merchant(db: Session, merchant_id: int) -> List[Service]:
    """获取商家的服务列表"""
    return db.query(Service).filter(
        Service.merchant_id == merchant_id,
        Service.status == ServiceStatus.ACTIVE
    ).all()


def get_active_services(db: Session, skip: int = 0, limit: int = 20) -> List[Service]:
    """获取活跃的服务列表"""
    return db.query(Service).filter(
        Service.status == ServiceStatus.ACTIVE
    ).offset(skip).limit(limit).all() 
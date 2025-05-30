from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.services import Service
from app.schemas.services import ServiceCreate, ServiceUpdate


def get_service(db: Session, service_id: int) -> Optional[Service]:
    return db.query(Service).filter(Service.service_id == service_id).first()

def get_services(db: Session, skip: int = 0, limit: int = 100) -> List[Service]:
    return db.query(Service).offset(skip).limit(limit).all()

def create_service(db: Session, service: ServiceCreate) -> Service:
    db_service = Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service 
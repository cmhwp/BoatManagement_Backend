from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.orders import Order
from app.schemas.orders import OrderCreate, OrderUpdate


def get_order(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.order_id == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    return db.query(Order).offset(skip).limit(limit).all()

def create_order(db: Session, user_id: int, order: OrderCreate) -> Order:
    db_order = Order(user_id=user_id, **order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order 
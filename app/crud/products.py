from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.agricultural_products import AgriculturalProduct
from app.schemas.products import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: int) -> Optional[AgriculturalProduct]:
    return db.query(AgriculturalProduct).filter(AgriculturalProduct.product_id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[AgriculturalProduct]:
    return db.query(AgriculturalProduct).offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate) -> AgriculturalProduct:
    db_product = AgriculturalProduct(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product 
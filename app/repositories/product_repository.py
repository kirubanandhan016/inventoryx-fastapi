from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


def get_product(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def get_product_by_sku(db: Session, sku: str) -> Product | None:
    return db.scalar(select(Product).where(Product.sku == sku))


def list_products(db: Session, offset: int = 0, limit: int = 100) -> list[Product]:
    return list(
        db.scalars(select(Product).order_by(Product.id).offset(offset).limit(limit))
    )

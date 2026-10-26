from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.repositories import product_repository
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, data: ProductCreate) -> Product:
    if product_repository.get_product_by_sku(db, data.sku):
        raise HTTPException(status_code=409, detail="SKU already exists")
    if data.category_id is not None and db.get(Category, data.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")

    product = Product(**data.model_dump())
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="SKU already exists") from None
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    product = product_repository.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    changes = data.model_dump(exclude_unset=True)
    new_sku = changes.get("sku")
    if new_sku and new_sku != product.sku:
        existing = product_repository.get_product_by_sku(db, new_sku)
        if existing is not None:
            raise HTTPException(status_code=409, detail="SKU already exists")
    category_id = changes.get("category_id")
    if category_id is not None and db.get(Category, category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in changes.items():
        setattr(product, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Product conflicts with existing data"
        ) from None
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> None:
    product = product_repository.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Product is referenced by existing records"
        ) from None

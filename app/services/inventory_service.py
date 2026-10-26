from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product


def adjust_inventory(
    db: Session, product_id: int, user_id: int, change: int, reason: str, note: str | None
) -> InventoryTransaction:
    if change == 0:
        raise HTTPException(status_code=422, detail="Inventory change cannot be zero")
    product = db.scalar(
        select(Product).where(Product.id == product_id).with_for_update()
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.quantity + change < 0:
        raise HTTPException(status_code=409, detail="Insufficient inventory")

    product.quantity += change
    transaction = InventoryTransaction(
        product_id=product_id,
        user_id=user_id,
        change=change,
        reason=reason,
        note=note,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

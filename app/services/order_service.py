from collections import Counter
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory_transaction import InventoryTransaction
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.repositories import order_repository
from app.schemas.order import OrderCreate


def create_order(db: Session, user_id: int, data: OrderCreate) -> Order:
    quantities = Counter(
        {item.product_id: 0 for item in data.items}
    )
    for item in data.items:
        quantities[item.product_id] += item.quantity

    products: dict[int, Product] = {}
    for product_id, quantity in quantities.items():
        product = db.scalar(
            select(Product).where(Product.id == product_id).with_for_update()
        )
        if product is None:
            raise HTTPException(
                status_code=404, detail=f"Product {product_id} not found"
            )
        if product.quantity < quantity:
            raise HTTPException(
                status_code=409,
                detail=f"Insufficient inventory for product {product_id}",
            )
        products[product_id] = product

    total = sum(
        (products[product_id].price * quantity for product_id, quantity in quantities.items()),
        start=Decimal("0.00"),
    )
    order = Order(user_id=user_id, total=total, status="placed")
    db.add(order)
    for product_id, quantity in quantities.items():
        product = products[product_id]
        product.quantity -= quantity
        order.items.append(
            OrderItem(
                product_id=product_id,
                quantity=quantity,
                unit_price=product.price,
            )
        )
        db.add(
            InventoryTransaction(
                product_id=product_id,
                user_id=user_id,
                change=-quantity,
                reason="order",
                note="Order stock deduction",
            )
        )

    db.commit()
    return order


def get_order(db: Session, order_id: int, user_id: int) -> Order:
    order = order_repository.get_order(db, order_id, user_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def list_orders(db: Session, user_id: int, offset: int = 0, limit: int = 100) -> list[Order]:
    return order_repository.list_orders(db, user_id, offset, limit)


def cancel_order(db: Session, order_id: int, user_id: int) -> Order:
    order = order_repository.get_order(db, order_id, user_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == "cancelled":
        raise HTTPException(status_code=409, detail="Order is already cancelled")

    for item in order.items:
        product = db.scalar(
            select(Product).where(Product.id == item.product_id).with_for_update()
        )
        if product is None:
            raise HTTPException(status_code=409, detail="An ordered product no longer exists")
        product.quantity += item.quantity
        db.add(
            InventoryTransaction(
                product_id=product.id,
                user_id=user_id,
                change=item.quantity,
                reason="order_cancellation",
                note=f"Order {order.id} cancellation",
            )
        )
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return order

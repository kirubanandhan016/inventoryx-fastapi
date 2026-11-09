from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order


def get_order(
    db: Session,
    order_id: int,
    user_id: int,
    *,
    for_update: bool = False,
) -> Order | None:
    statement = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id, Order.user_id == user_id)
    )
    if for_update:
        # Serialize state transitions such as cancellation on PostgreSQL.
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_orders(db: Session, user_id: int, offset: int = 0, limit: int = 100) -> list[Order]:
    return list(
        db.scalars(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.user_id == user_id)
            .order_by(Order.id.desc())
            .offset(offset)
            .limit(limit)
        )
    )

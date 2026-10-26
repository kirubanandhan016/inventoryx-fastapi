from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api_dependencies import get_current_user
from app.database.session import get_db
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderCreate, OrderRead
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Order:
    return order_service.create_order(db, user.id, data)


@router.get("", response_model=list[OrderRead])
def read_orders(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Order]:
    return order_service.list_orders(db, user.id, offset, limit)


@router.get("/{order_id}", response_model=OrderRead)
def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Order:
    return order_service.get_order(db, order_id, user.id)


@router.post("/{order_id}/cancel", response_model=OrderRead)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Order:
    return order_service.cancel_order(db, order_id, user.id)

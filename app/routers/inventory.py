from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api_dependencies import get_current_user
from app.database.session import get_db
from app.models.inventory_transaction import InventoryTransaction
from app.models.user import User
from app.services.inventory_service import adjust_inventory

router = APIRouter(prefix="/inventory", tags=["inventory"])


class InventoryAdjustment(BaseModel):
    change: int
    reason: Literal["restock", "correction", "damage", "other"]
    note: str | None = Field(default=None, max_length=500)

    @field_validator("change")
    @classmethod
    def change_must_not_be_zero(cls, value: int) -> int:
        if value == 0:
            raise ValueError("Inventory change cannot be zero")
        return value


class InventoryTransactionRead(BaseModel):
    id: int
    product_id: int
    user_id: int
    change: int
    reason: str
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.post("/{product_id}/adjust", response_model=InventoryTransactionRead)
def adjust_product_inventory(
    product_id: int,
    data: InventoryAdjustment,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> InventoryTransaction:
    return adjust_inventory(
        db, product_id, user.id, data.change, data.reason, data.note
    )


@router.get("/transactions", response_model=list[InventoryTransactionRead])
def read_inventory_transactions(
    product_id: int | None = Query(default=None, gt=0),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[InventoryTransaction]:
    query = select(InventoryTransaction).order_by(InventoryTransaction.id.desc())
    if product_id is not None:
        query = query.where(InventoryTransaction.product_id == product_id)
    return list(db.scalars(query.offset(offset).limit(limit)))

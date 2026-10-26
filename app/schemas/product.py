from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    quantity: int = Field(default=0, ge=0)
    category_id: int | None = Field(default=None, gt=0)


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )
    category_id: int | None = Field(default=None, gt=0)


class ProductRead(BaseModel):
    id: int
    sku: str
    name: str
    description: str | None
    price: Decimal
    quantity: int
    category_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

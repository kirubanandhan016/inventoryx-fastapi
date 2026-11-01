from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    quantity: int = Field(default=0, ge=0)
    category_id: int | None = Field(default=None, gt=0)

    @field_validator("sku", "name", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )
    category_id: int | None = Field(default=None, gt=0)

    @field_validator("sku", "name", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def reject_null_for_required_fields(self) -> "ProductUpdate":
        for field_name in ("sku", "name", "price"):
            if field_name in self.model_fields_set and getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


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

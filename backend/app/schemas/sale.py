from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SaleStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"


class SaleItemCreate(BaseModel):
    product_id: int = Field(gt=0)

    quantity: Decimal = Field(
        gt=0,
        decimal_places=3,
    )

    unit_price: Decimal = Field(
        gt=0,
        decimal_places=2,
    )


class SaleCreate(BaseModel):
    customer_id: int = Field(gt=0)
    warehouse_id: int = Field(gt=0)

    reference: str | None = Field(
        default=None,
        max_length=100,
    )

    notes: str | None = Field(
        default=None,
        max_length=500,
    )

    items: list[SaleItemCreate] = Field(
        min_length=1,
    )


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal

    model_config = ConfigDict(
        from_attributes=True,
    )


class SaleResponse(BaseModel):
    id: int
    customer_id: int
    warehouse_id: int
    status: SaleStatus
    sale_date: datetime
    reference: str | None
    notes: str | None
    items: list[SaleItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
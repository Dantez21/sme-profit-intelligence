from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PurchaseStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"


class PurchaseItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(
        gt=0,
        decimal_places=3,
    )
    unit_cost: Decimal = Field(
        gt=0,
        decimal_places=2,
    )


class PurchaseCreate(BaseModel):
    supplier_id: int = Field(gt=0)
    warehouse_id: int = Field(gt=0)

    reference: str | None = Field(
        default=None,
        max_length=100,
    )

    notes: str | None = Field(
        default=None,
        max_length=500,
    )

    items: list[PurchaseItemCreate] = Field(
        min_length=1,
    )


class PurchaseItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_cost: Decimal

    model_config = ConfigDict(
        from_attributes=True,
    )


class PurchaseResponse(BaseModel):
    id: int
    supplier_id: int
    warehouse_id: int
    status: PurchaseStatus
    purchase_date: datetime
    reference: str | None
    notes: str | None
    items: list[PurchaseItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
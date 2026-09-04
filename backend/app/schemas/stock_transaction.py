from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StockTransactionType(str, Enum):
    OPENING = "opening"
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"


class StockTransactionCreate(BaseModel):
    product_id: int = Field(gt=0)
    warehouse_id: int = Field(gt=0)

    transaction_type: StockTransactionType

    quantity: Decimal = Field(
        gt=0,
        decimal_places=3,
    )

    reference: str | None = Field(
        default=None,
        max_length=100,
    )

    notes: str | None = None


class StockTransactionResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    transaction_type: StockTransactionType
    quantity: Decimal
    reference: str | None
    notes: str | None
    transaction_date: datetime
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

class StockBalanceResponse(BaseModel):
    product_id: int
    warehouse_id: int
    stock_quantity: Decimal
    unit: str

    model_config = ConfigDict(
        from_attributes=True,
    )
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    sku: str = Field(min_length=2, max_length=50)
    description: str | None = None
    category: str = Field(min_length=2, max_length=100)
    unit: str = Field(default="pcs", max_length=20)

    cost_price: Decimal = Field(gt=0, decimal_places=2)
    selling_price: Decimal = Field(gt=0, decimal_places=2)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = None
    category: str | None = Field(default=None, min_length=2, max_length=100)
    unit: str | None = Field(default=None, max_length=20)

    cost_price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    selling_price: Decimal | None = Field(default=None, gt=0, decimal_places=2)


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
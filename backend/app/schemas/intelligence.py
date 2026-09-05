from decimal import Decimal

from pydantic import BaseModel


class ProfitSummaryResponse(BaseModel):
    revenue: Decimal
    cogs: Decimal
    gross_profit: Decimal
    gross_margin: Decimal


class ProductProfitabilityResponse(BaseModel):
    product_id: int
    quantity_sold: Decimal
    revenue: Decimal
    cogs: Decimal
    gross_profit: Decimal
    gross_margin: Decimal


class InventoryProductResponse(BaseModel):
    product_id: int
    product_name: str
    sku: str
    warehouse_id: int
    warehouse_name: str
    current_stock: Decimal
    reorder_level: Decimal
    stock_value: Decimal
    low_stock: bool


class InventoryIntelligenceResponse(BaseModel):
    total_stock_value: Decimal
    low_stock_products: int
    products: list[InventoryProductResponse]
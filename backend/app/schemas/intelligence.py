from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProfitSummaryResponse(BaseModel):
    revenue: Decimal
    cogs: Decimal
    gross_profit: Decimal
    gross_margin: Decimal

    model_config = ConfigDict(
        from_attributes=True,
    )

class ProductProfitabilityResponse(BaseModel):
    product_id: int
    quantity_sold: Decimal
    revenue: Decimal
    cogs: Decimal
    gross_profit: Decimal
    gross_margin: Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.intelligence import (
    InventoryIntelligenceResponse,
    ProductProfitabilityResponse,
    ProfitSummaryResponse,
)
from app.services.profit_intelligence import (
    get_inventory_intelligence,
    get_product_profitability,
    get_profit_summary,
)


router = APIRouter(
    prefix="/api/v1/intelligence",
    tags=["Intelligence"],
)


@router.get(
    "/profit-summary",
    response_model=ProfitSummaryResponse,
)
def profit_summary(
    db: Session = Depends(get_db),
):
    return get_profit_summary(db)


@router.get(
    "/product-profitability",
    response_model=list[ProductProfitabilityResponse],
)
def product_profitability(
    db: Session = Depends(get_db),
):
    return get_product_profitability(db)


@router.get(
    "/inventory",
    response_model=InventoryIntelligenceResponse,
)
def inventory_intelligence(
    db: Session = Depends(get_db),
):
    return get_inventory_intelligence(db)
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.sale import Sale, SaleItem


def get_profit_summary(db: Session) -> dict:
    revenue = db.scalar(
        select(
            func.coalesce(
                func.sum(
                    SaleItem.quantity * SaleItem.unit_price
                ),
                0,
            )
        )
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.status == "submitted")
    )

    cogs = db.scalar(
        select(
            func.coalesce(
                func.sum(
                    SaleItem.quantity * SaleItem.unit_cost
                ),
                0,
            )
        )
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.status == "submitted")
    )

    revenue = Decimal(revenue)
    cogs = Decimal(cogs)

    gross_profit = revenue - cogs

    if revenue > 0:
        gross_margin = (
            gross_profit / revenue
        ) * Decimal("100")
    else:
        gross_margin = Decimal("0")

    return {
        "revenue": revenue,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "gross_margin": gross_margin,
    }

    
def get_product_profitability(db: Session) -> list[dict]:
    results = db.execute(
        select(
            SaleItem.product_id,
            func.sum(SaleItem.quantity).label("quantity_sold"),
            func.sum(
                SaleItem.quantity * SaleItem.unit_price
            ).label("revenue"),
            func.sum(
                SaleItem.quantity * SaleItem.unit_cost
            ).label("cogs"),
        )
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.status == "submitted")
        .group_by(SaleItem.product_id)
        .order_by(
            func.sum(
                SaleItem.quantity * SaleItem.unit_price
            ).desc()
        )
    ).all()

    profitability = []

    for row in results:
        quantity_sold = Decimal(row.quantity_sold)
        revenue = Decimal(row.revenue)
        cogs = Decimal(row.cogs)

        gross_profit = revenue - cogs

        if revenue > 0:
            gross_margin = (
                gross_profit / revenue
            ) * Decimal("100")
        else:
            gross_margin = Decimal("0")

        profitability.append(
            {
                "product_id": row.product_id,
                "quantity_sold": quantity_sold,
                "revenue": revenue,
                "cogs": cogs,
                "gross_profit": gross_profit,
                "gross_margin": gross_margin,
            }
        )

    return profitability
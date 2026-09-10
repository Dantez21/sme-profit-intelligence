from datetime import date, datetime, time, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.stock_transaction import StockTransaction
from app.models.warehouse import Warehouse


def apply_sale_date_filter(
    query,
    start_date: date | None = None,
    end_date: date | None = None,
):
    if start_date is not None:
        start_datetime = datetime.combine(
            start_date,
            time.min,
            tzinfo=timezone.utc,
        )
        query = query.where(
            Sale.sale_date >= start_datetime,
        )

    if end_date is not None:
        end_datetime = datetime.combine(
            end_date,
            time.max,
            tzinfo=timezone.utc,
        )
        query = query.where(
            Sale.sale_date <= end_datetime,
        )

    return query


def get_profit_summary(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    revenue_query = (
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

    revenue_query = apply_sale_date_filter(
        revenue_query,
        start_date,
        end_date,
    )

    revenue = db.scalar(revenue_query)

    cogs_query = (
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

    cogs_query = apply_sale_date_filter(
        cogs_query,
        start_date,
        end_date,
    )

    cogs = db.scalar(cogs_query)

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
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            Product.sku.label("sku"),
            func.sum(SaleItem.quantity).label("quantity_sold"),
            func.sum(
                SaleItem.quantity * SaleItem.unit_price
            ).label("revenue"),
            func.sum(
                SaleItem.quantity * SaleItem.unit_cost
            ).label("cogs"),
        )
        .join(
            Sale,
            SaleItem.sale_id == Sale.id,
        )
        .join(
            Product,
            SaleItem.product_id == Product.id,
        )
        .where(
            Sale.status == "submitted",
        )
        .group_by(
            Product.id,
            Product.name,
            Product.sku,
        )
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
                "product_name": row.product_name,
                "sku": row.sku,
                "quantity_sold": quantity_sold,
                "revenue": revenue,
                "cogs": cogs,
                "gross_profit": gross_profit,
                "gross_margin": gross_margin,
            }
        )

    return profitability

def get_inventory_intelligence(db: Session) -> dict:
    results = db.execute(
        select(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            Product.sku.label("sku"),
            Product.cost_price.label("cost_price"),
            Product.reorder_level.label("reorder_level"),
            Warehouse.id.label("warehouse_id"),
            Warehouse.name.label("warehouse_name"),
            func.coalesce(
                func.sum(StockTransaction.quantity),
                0,
            ).label("current_stock"),
        )
        .select_from(Product)
        .join(
            Warehouse,
            Warehouse.is_active.is_(True),
        )
        .outerjoin(
            StockTransaction,
            (
                StockTransaction.product_id
                == Product.id
            )
            & (
                StockTransaction.warehouse_id
                == Warehouse.id
            ),
        )
        .group_by(
            Product.id,
            Product.name,
            Product.sku,
            Product.cost_price,
            Product.reorder_level,
            Warehouse.id,
            Warehouse.name,
        )
        .order_by(
            Product.name,
            Warehouse.name,
        )
    ).all()

    products = []
    total_stock_value = Decimal("0")
    low_stock_count = 0

    for row in results:
        current_stock = Decimal(row.current_stock)
        reorder_level = Decimal(row.reorder_level)
        cost_price = Decimal(row.cost_price)

        stock_value = (
            current_stock * cost_price
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        low_stock = current_stock <= reorder_level

        total_stock_value += stock_value

        if low_stock:
            low_stock_count += 1

        products.append(
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "sku": row.sku,
                "warehouse_id": row.warehouse_id,
                "warehouse_name": row.warehouse_name,
                "current_stock": current_stock,
                "reorder_level": reorder_level,
                "stock_value": stock_value,
                "low_stock": low_stock,
            }
        )

    total_stock_value = total_stock_value.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    return {
        "total_stock_value": total_stock_value,
        "low_stock_products": low_stock_count,
        "products": products,
    }


def get_revenue_trend(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict]:
    year_expression = func.extract(
        "year",
        Sale.sale_date,
    )

    month_expression = func.extract(
        "month",
        Sale.sale_date,
    )

    trend_query = (
        select(
            year_expression.label("year"),
            month_expression.label("month"),
            func.coalesce(
                func.sum(
                    SaleItem.quantity
                    * SaleItem.unit_price
                ),
                0,
            ).label("revenue"),
            func.coalesce(
                func.sum(
                    SaleItem.quantity
                    * SaleItem.unit_cost
                ),
                0,
            ).label("cogs"),
        )
        .join(
            Sale,
            SaleItem.sale_id == Sale.id,
        )
        .where(
            Sale.status == "submitted",
        )
    )

    trend_query = apply_sale_date_filter(
        trend_query,
        start_date,
        end_date,
    )

    trend_query = (
        trend_query
        .group_by(
            year_expression,
            month_expression,
        )
        .order_by(
            year_expression,
            month_expression,
        )
    )

    results = db.execute(trend_query).all()

    trend = []

    for row in results:
        revenue = Decimal(row.revenue)
        cogs = Decimal(row.cogs)
        gross_profit = revenue - cogs

        period = (
            f"{int(row.year):04d}-"
            f"{int(row.month):02d}"
        )

        trend.append(
            {
                "period": period,
                "revenue": revenue.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                ),
                "cogs": cogs.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                ),
                "gross_profit": gross_profit.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                ),
            }
        )

    return trend


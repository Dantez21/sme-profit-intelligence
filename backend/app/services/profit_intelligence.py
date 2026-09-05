from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.stock_transaction import StockTransaction
from app.models.warehouse import Warehouse


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
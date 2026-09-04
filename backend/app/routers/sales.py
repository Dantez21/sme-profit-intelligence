from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.stock_transaction import StockTransaction
from app.models.warehouse import Warehouse
from app.schemas.sale import (
    SaleCreate,
    SaleResponse,
    SaleStatus,
)


router = APIRouter(
    prefix="/api/v1/sales",
    tags=["Sales"],
)


def get_current_stock(
    product_id: int,
    warehouse_id: int,
    db: Session,
) -> Decimal:
    balance = db.scalar(
        select(
            func.coalesce(
                func.sum(StockTransaction.quantity),
                0,
            )
        ).where(
            StockTransaction.product_id == product_id,
            StockTransaction.warehouse_id == warehouse_id,
        )
    )

    return Decimal(balance)


@router.post(
    "",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
):
    customer = db.get(
        Customer,
        sale_data.customer_id,
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    warehouse = db.get(
        Warehouse,
        sale_data.warehouse_id,
    )

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found.",
        )

    sale = Sale(
        customer_id=sale_data.customer_id,
        warehouse_id=sale_data.warehouse_id,
        status=SaleStatus.DRAFT.value,
        reference=sale_data.reference,
        notes=sale_data.notes,
    )

    for item_data in sale_data.items:
        product = db.get(
            Product,
            item_data.product_id,
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Product {item_data.product_id} not found."
                ),
            )

        sale.items.append(
            SaleItem(
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
            )
        )

    db.add(sale)
    db.commit()
    db.refresh(sale)

    return sale


@router.get(
    "",
    response_model=list[SaleResponse],
)
def list_sales(
    db: Session = Depends(get_db),
):
    sales = db.scalars(
        select(Sale).order_by(Sale.id.desc())
    ).all()

    return sales


@router.get(
    "/{sale_id}",
    response_model=SaleResponse,
)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
):
    sale = db.get(
        Sale,
        sale_id,
    )

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found.",
        )

    return sale


@router.post(
    "/{sale_id}/submit",
    response_model=SaleResponse,
)
def submit_sale(
    sale_id: int,
    db: Session = Depends(get_db),
):
    sale = db.get(
        Sale,
        sale_id,
    )

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found.",
        )

    if sale.status == SaleStatus.SUBMITTED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sale has already been submitted.",
        )

    if not sale.items:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot submit a sale without items.",
        )

    # Validate ALL items before creating any stock transaction.
    for item in sale.items:
        current_stock = get_current_stock(
            item.product_id,
            sale.warehouse_id,
            db,
        )

        if item.quantity > current_stock:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Insufficient stock for product "
                    f"{item.product_id}. "
                    f"Available stock: {current_stock}."
                ),
            )

    # Only after every item passes validation do we change stock.
    for item in sale.items:
        stock_transaction = StockTransaction(
            product_id=item.product_id,
            warehouse_id=sale.warehouse_id,
            transaction_type="sale",
            quantity=-Decimal(item.quantity),
            reference=f"SALE-{sale.id}",
            notes=sale.reference,
        )

        db.add(stock_transaction)

    sale.status = SaleStatus.SUBMITTED.value

    db.commit()
    db.refresh(sale)

    return sale
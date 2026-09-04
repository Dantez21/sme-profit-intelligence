from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.models.stock_transaction import StockTransaction
from app.models.warehouse import Warehouse
from app.schemas.stock_transaction import (
    StockBalanceResponse,
    StockTransactionCreate,
    StockTransactionResponse,
    StockTransactionType,
)

router = APIRouter(
    prefix="/api/v1/stock-transactions",
    tags=["Stock Transactions"],
)


INBOUND_TYPES = {
    StockTransactionType.OPENING,
    StockTransactionType.PURCHASE,
    StockTransactionType.TRANSFER_IN,
}

OUTBOUND_TYPES = {
    StockTransactionType.SALE,
    StockTransactionType.TRANSFER_OUT,
}


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
    response_model=StockTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_stock_transaction(
    transaction_data: StockTransactionCreate,
    db: Session = Depends(get_db),
):
    product = db.get(
        Product,
        transaction_data.product_id,
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    warehouse = db.get(
        Warehouse,
        transaction_data.warehouse_id,
    )

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found.",
        )

    current_stock = get_current_stock(
        transaction_data.product_id,
        transaction_data.warehouse_id,
        db,
    )

    if transaction_data.transaction_type in OUTBOUND_TYPES:
        if transaction_data.quantity > current_stock:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Insufficient stock. Available stock: "
                    f"{current_stock}."
                ),
            )

        quantity = -transaction_data.quantity

    elif transaction_data.transaction_type in INBOUND_TYPES:
        quantity = transaction_data.quantity

    else:
        quantity = transaction_data.quantity

    transaction = StockTransaction(
        product_id=transaction_data.product_id,
        warehouse_id=transaction_data.warehouse_id,
        transaction_type=transaction_data.transaction_type.value,
        quantity=quantity,
        reference=transaction_data.reference,
        notes=transaction_data.notes,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


@router.get(
    "",
    response_model=list[StockTransactionResponse],
)
def list_stock_transactions(
    db: Session = Depends(get_db),
):
    transactions = db.scalars(
        select(StockTransaction).order_by(
            StockTransaction.id.desc()
        )
    ).all()

    return transactions


@router.get(
    "/stock",
    response_model=StockBalanceResponse,
)
def get_stock_balance(
    product_id: int,
    warehouse_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    warehouse = db.get(Warehouse, warehouse_id)

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found.",
        )

    current_stock = get_current_stock(
        product_id,
        warehouse_id,
        db,
    )

    return {
        "product_id": product_id,
        "warehouse_id": warehouse_id,
        "stock_quantity": current_stock,
        "unit": product.unit,
    }
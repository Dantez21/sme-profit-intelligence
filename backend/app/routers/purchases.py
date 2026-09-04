from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.models.purchase import Purchase, PurchaseItem
from app.models.stock_transaction import StockTransaction
from app.models.supplier import Supplier
from app.models.warehouse import Warehouse
from app.schemas.purchase import (
    PurchaseCreate,
    PurchaseResponse,
    PurchaseStatus,
)


router = APIRouter(
    prefix="/api/v1/purchases",
    tags=["Purchases"],
)


@router.post(
    "",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase(
    purchase_data: PurchaseCreate,
    db: Session = Depends(get_db),
):
    supplier = db.get(
        Supplier,
        purchase_data.supplier_id,
    )

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found.",
        )

    warehouse = db.get(
        Warehouse,
        purchase_data.warehouse_id,
    )

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found.",
        )

    purchase = Purchase(
        supplier_id=purchase_data.supplier_id,
        warehouse_id=purchase_data.warehouse_id,
        status=PurchaseStatus.DRAFT.value,
        reference=purchase_data.reference,
        notes=purchase_data.notes,
    )

    for item_data in purchase_data.items:
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

        purchase.items.append(
            PurchaseItem(
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_cost=item_data.unit_cost,
            )
        )

    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    return purchase


@router.get(
    "",
    response_model=list[PurchaseResponse],
)
def list_purchases(
    db: Session = Depends(get_db),
):
    purchases = db.scalars(
        select(Purchase).order_by(Purchase.id.desc())
    ).all()

    return purchases


@router.get(
    "/{purchase_id}",
    response_model=PurchaseResponse,
)
def get_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
):
    purchase = db.get(Purchase, purchase_id)

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase not found.",
        )

    return purchase


@router.post(
    "/{purchase_id}/submit",
    response_model=PurchaseResponse,
)
def submit_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
):
    purchase = db.get(
        Purchase,
        purchase_id,
    )

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase not found.",
        )

    if purchase.status == PurchaseStatus.SUBMITTED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Purchase has already been submitted.",
        )

    if not purchase.items:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot submit a purchase without items.",
        )

    for item in purchase.items:
        stock_transaction = StockTransaction(
            product_id=item.product_id,
            warehouse_id=purchase.warehouse_id,
            transaction_type="purchase",
            quantity=Decimal(item.quantity),
            reference=f"PURCHASE-{purchase.id}",
            notes=purchase.reference,
        )

        db.add(stock_transaction)

    purchase.status = PurchaseStatus.SUBMITTED.value

    db.commit()
    db.refresh(purchase)

    return purchase
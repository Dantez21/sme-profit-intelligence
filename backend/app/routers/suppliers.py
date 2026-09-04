from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import (
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)


router = APIRouter(
    prefix="/api/v1/suppliers",
    tags=["Suppliers"],
)


@router.post(
    "",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
):
    existing_supplier = db.scalar(
        select(Supplier).where(
            Supplier.code == supplier_data.code
        )
    )

    if existing_supplier:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A supplier with this code already exists.",
        )

    supplier = Supplier(**supplier_data.model_dump())

    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return supplier


@router.get(
    "",
    response_model=list[SupplierResponse],
)
def list_suppliers(
    db: Session = Depends(get_db),
):
    suppliers = db.scalars(
        select(Supplier).order_by(Supplier.id.desc())
    ).all()

    return suppliers


@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse,
)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
):
    supplier = db.get(Supplier, supplier_id)

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found.",
        )

    return supplier


@router.put(
    "/{supplier_id}",
    response_model=SupplierResponse,
)
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
):
    supplier = db.get(Supplier, supplier_id)

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found.",
        )

    update_data = supplier_data.model_dump(
        exclude_unset=True
    )

    if "code" in update_data:
        existing_supplier = db.scalar(
            select(Supplier).where(
                Supplier.code == update_data["code"],
                Supplier.id != supplier_id,
            )
        )

        if existing_supplier:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A supplier with this code already exists.",
            )

    for field, value in update_data.items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)

    return supplier


@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
):
    supplier = db.get(Supplier, supplier_id)

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found.",
        )

    db.delete(supplier)
    db.commit()
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.warehouse import Warehouse
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseResponse,
    WarehouseUpdate,
)


router = APIRouter(
    prefix="/api/v1/warehouses",
    tags=["Warehouses"],
)


@router.post(
    "",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_warehouse(
    warehouse_data: WarehouseCreate,
    db: Session = Depends(get_db),
):
    existing_warehouse = db.scalar(
        select(Warehouse).where(
            (Warehouse.name == warehouse_data.name)
            | (Warehouse.code == warehouse_data.code)
        )
    )

    if existing_warehouse:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A warehouse with this name or code already exists.",
        )

    warehouse = Warehouse(**warehouse_data.model_dump())

    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)

    return warehouse


@router.get(
    "",
    response_model=list[WarehouseResponse],
)
def list_warehouses(
    db: Session = Depends(get_db),
):
    warehouses = db.scalars(
        select(Warehouse).order_by(Warehouse.id.desc())
    ).all()

    return warehouses


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseResponse,
)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
):
    warehouse = db.get(Warehouse, warehouse_id)

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found.",
        )

    return warehouse


@router.put(
    "/{warehouse_id}",
    response_model=WarehouseResponse,
)
def update_warehouse(
    warehouse_id: int,
    warehouse_data: WarehouseUpdate,
    db: Session = Depends(get_db),
):
    warehouse = db.get(Warehouse, warehouse_id)

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found.",
        )

    update_data = warehouse_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing_warehouse = db.scalar(
            select(Warehouse).where(
                Warehouse.name == update_data["name"],
                Warehouse.id != warehouse_id,
            )
        )

        if existing_warehouse:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A warehouse with this name already exists.",
            )

    if "code" in update_data:
        existing_warehouse = db.scalar(
            select(Warehouse).where(
                Warehouse.code == update_data["code"],
                Warehouse.id != warehouse_id,
            )
        )

        if existing_warehouse:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A warehouse with this code already exists.",
            )

    for field, value in update_data.items():
        setattr(warehouse, field, value)

    db.commit()
    db.refresh(warehouse)

    return warehouse


@router.delete(
    "/{warehouse_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
):
    warehouse = db.get(Warehouse, warehouse_id)

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found.",
        )

    db.delete(warehouse)
    db.commit()
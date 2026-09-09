from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.models.product import Product
from app.routers.products import router as product_router
from app.routers.categories import router as category_router
from app.routers.warehouses import router as warehouse_router
from app.routers.customers import router as customer_router
from app.routers.suppliers import router as supplier_router
from app.routers.purchases import router as purchase_router
from app.routers.sales import router as sale_router
from app.routers.stock_transactions import (
    router as stock_transaction_router,
)
from app.routers.intelligence import router as intelligence_router


# Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SME Profit & Inventory Intelligence API",
    description=(
        "Backend API for SME inventory, sales, "
        "purchasing and profit intelligence."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(product_router)
app.include_router(category_router)
app.include_router(warehouse_router)
app.include_router(customer_router)
app.include_router(supplier_router)
app.include_router(purchase_router)
app.include_router(sale_router)
app.include_router(stock_transaction_router)
app.include_router(intelligence_router)


@app.get("/")
def root():
    return {
        "message": "SME Profit & Inventory Intelligence API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }
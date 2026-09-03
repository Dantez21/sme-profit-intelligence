from fastapi import FastAPI

app = FastAPI(
    title="SME Profit & Inventory Intelligence API",
    description="Backend API for SME inventory, sales, purchasing and profit intelligence.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "SME Profit & Inventory Intelligence API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
from fastapi import FastAPI

from app.api.routes.transactions import router as transactions_router
from app.api.routes.alerts import router as alerts_router



app = FastAPI(
    title="Fraud Detection System",
    version="1.0"
)

# Register Routes
app.include_router(transactions_router)
app.include_router(alerts_router)


# Health Check
@app.get("/")
def root():
    return {"message": "Fraud Detection API is running"}
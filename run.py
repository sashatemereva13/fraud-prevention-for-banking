from fastapi import FastAPI

from app.api.routes.transactions import router as transactions_router


app = FastAPI(
    title="Fraud Detection System",
    version="1.0"
)

# Register Routes
app.include_router(transactions_router)


# Health Check
@app.get("/")
def root():
    return {"message": "Fraud Detection API is running"}
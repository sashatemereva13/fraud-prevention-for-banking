from fastapi import FastAPI

from app.api.routes.transactions import router as transactions_router
from app.api.routes.users import router as users_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.dashboard import router as dashboard_router

# FASTAPI APP
app = FastAPI(
    title="Fraud Detection System",
    version="1.0",
    description="Real-time fraud detection using MongoDB, Redis, and Neo4j"
)

# REGISTER ROUTES
app.include_router(transactions_router)
app.include_router(users_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)

# HEALTH CHECK
@app.get("/")
def root():
    return {
        "message": "Fraud Detection API is running"
    }



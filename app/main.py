from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.transactions import router as transactions_router
from app.api.routes.users import router as users_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.dashboard import router as dashboard_router
from app.db.neo4j_client import neo4j_client
import asyncio
from neo4j.exceptions import ServiceUnavailable


@asynccontextmanager
async def lifespan(app: FastAPI):
    for attempt in range(10):
        try:
            await neo4j_client.connect()
            break
        except ServiceUnavailable:
            if attempt < 9:
                print(f"Neo4j not ready, retrying ({attempt + 1}/10)...")
                await asyncio.sleep(3)
            else:
                raise
    try:
        yield
    finally:
        await neo4j_client.close()

# FASTAPI APP
app = FastAPI(
    title="Fraud Detection System",
    version="1.0",
    description="Real-time fraud detection using MongoDB, Redis, and Neo4j",
    lifespan=lifespan
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


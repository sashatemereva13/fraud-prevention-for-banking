from fastapi import APIRouter
from pydantic import BaseModel
from app.services.redis_behavior_service import compute_risk
from app.core.graph_checks import check_circular_ring, check_device_sharing

router = APIRouter()

class TransactionRequest(BaseModel):
    user_id: str
    device: str
    location: str

@router.post("/analyze-transaction")
def analyse_transaction(req: TransactionRequest):
    return compute_risk(req.user_id, req.device, req.location)

from app.models.transactions import TransactionCreate

from app.services.transaction_service import (
    create_transaction,
    suspicious_transaction_frequency,
    daily_spending_analysis
)


# CREATE TRANSACTION
@router.post("/transactions")
async def add_transaction(transaction: TransactionCreate):
    return await create_transaction(transaction)


# AGGREGATION 1
@router.get("/analytics/suspicious-transactions")
def get_suspicious_transactions():
    return suspicious_transaction_frequency()


# AGGREGATION 2
@router.get("/analytics/daily-spending")
def get_daily_spending():
    return daily_spending_analysis()


@router.get("/transactions/graph/ring/{account_id}")
async def inspect_ring(account_id: str):
    """check if an account is in a transfer ring."""
    result = await check_circular_ring(account_id)
    return {"account_id": account_id, **result}


@router.get("/transactions/graph/device/{fingerprint}")
async def inspect_device(fingerprint: str):
    """how many users share a device fingerprint."""
    result = await check_device_sharing(fingerprint)
    return {"fingerprint": fingerprint, **result}

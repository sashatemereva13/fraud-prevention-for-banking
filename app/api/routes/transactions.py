from fastapi import APIRouter
from pydantic import BaseModel
from app.services.redis_behavior_service import compute_risk

router = APIRouter()

class TransactionRequest(BaseModel):
    user_id: str
    device: str
    location: str

@router.post("/analyze-transaction")
def analyse_transaction(req: TransactionRequest):
    return compute_risk(req.user_id, req.device, req.location)

from app.services.transaction_service import (
    suspicious_transaction_frequency,
    daily_spending_analysis
)

router = APIRouter()


# MongoDB Analytics Routes
@router.get("/analytics/suspicious-transactions")
def get_suspicious_transactions():
    return suspicious_transaction_frequency()


@router.get("/analytics/daily-spending")
def get_daily_spending():
    return daily_spending_analysis()

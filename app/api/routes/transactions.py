from fastapi import APIRouter

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
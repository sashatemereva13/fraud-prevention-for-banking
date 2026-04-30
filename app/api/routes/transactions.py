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
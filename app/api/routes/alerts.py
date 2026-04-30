from fastapi import APIRouter

from app.services.alert_service import get_all_alerts

router = APIRouter()


@router.get("/alerts")
def fetch_alerts():
    return get_all_alerts()
from fastapi import APIRouter
from app.services.redis_behavior_service import check_new_device, check_velocity

router = APIRouter()

@router.post("/test-redis")
def test_redis(user_id: str, device: str):
    velocity_flag = check_velocity(user_id, "tx_test")
    device_flag = check_new_device(user_id, device)

    return {
        "velocity_flag": velocity_flag,
        "new_device": device_flag
    }
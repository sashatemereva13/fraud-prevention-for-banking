from redis import Redis
from app.config import get_settings

settings = get_settings()

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)
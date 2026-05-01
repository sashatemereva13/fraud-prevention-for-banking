from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME = "fraud-detection"
    DEBUG = False

    MONGO_URI= "mongodb://localhost:27017"
    MONGO_DB = "fraud_db"

    REDIS_URL = "redis://localhost:6379"

    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD: str

    NEO4J_MAX_CONNECTION_POOL= 50
    NEO4J_CONNECTION_TIMEOUT = 30

    # ── risk thresholds
    RISK_SCORE_ALERT_THRESHOLD= 0.7
    RISK_SCORE_BLOCK_THRESHOLD = 0.9

    GRAPH_RING_MAX_HOPS= 5
    GRAPH_DEVICE_SHARE_LIMIT = 3

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

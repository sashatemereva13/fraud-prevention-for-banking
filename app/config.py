from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "fraud-detection"
    APP_DEBUG: bool = False

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "fraud_db"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379"

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str

    NEO4J_MAX_CONNECTION_POOL: int = 50
    NEO4J_CONNECTION_TIMEOUT: int = 30

    # ── risk thresholds
    RISK_SCORE_ALERT_THRESHOLD: float = 0.7
    RISK_SCORE_BLOCK_THRESHOLD: float = 0.9

    GRAPH_RING_MAX_HOPS: int = 5
    GRAPH_DEVICE_SHARE_LIMIT: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()

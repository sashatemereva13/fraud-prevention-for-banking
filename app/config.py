from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "fraud-detection"
    DEBUG: bool = False

    MONGO_URI: str = "mongodb://mongodb:27017"
    MONGO_DB: str = "fraud_db"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str

    NEO4J_MAX_CONNECTION_POOL: int = 50
    NEO4J_CONNECTION_TIMEOUT: int = 30

    RISK_SCORE_ALERT_THRESHOLD: float = 0.7
    RISK_SCORE_BLOCK_THRESHOLD: float = 0.9

    GRAPH_RING_MAX_HOPS: int = 5
    GRAPH_DEVICE_SHARE_LIMIT: int = 3


@lru_cache()
def get_settings() -> Settings:
    return Settings()
@property
def REDIS_URL(self) -> str:
    return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
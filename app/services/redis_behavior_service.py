import time
from app.db.redis_client import redis_client

def check_velocity(user_id: str, transaction_id: str, window_seconds: int = 60, max_tx: int = 5) -> bool:
    """
    detecs if a user performs too many transctions
    in a short time frame (window).

    uses redis sorted sets:
    - key: user:{user_id}:recent_txs
    - score: timestamp
    - member: transaction_id
    """

    key = f"user:{user_id}:recent_txs"
    now = time.time()

    # add transaction with timestamp
    redis_client.zadd(key, {transaction_id: now})

    # remove transactions outside the time frame
    redis_client.zremrangebyscore(key, 0, now - window_seconds)

    # count remaining tranactions
    tx_count = redis_client.zcard(key)

    # return anomaly
    return tx_count > max_tx



def check_new_device(user_id: str, device: str) -> bool:
    """
    Detects if the user's device is new

    uses redis sets:
    - key: user:{user_id}:devices
    """

    key = f"user:{user_id}:devices"

    is_new = not redis_client.sismember(key, device)

    # store device for future reference
    redis_client.sadd(key, device)

    return is_new
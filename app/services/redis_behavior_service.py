import time
from app.db.redis_client import redis_client
import uuid

# ============================
# CONFIGURATION
# ============================
RISK_WEIGHTS = {
    "velocity": 50,
    "new_device": 30,
    "geo_anomaly": 40,
    "cooldown_violation": 20,
    "new_ip": 25,
}

SUSPICIOUS_THRESHOLD = 60


# ==========================
# VELOCITY CHECK
# ==========================

def check_velocity(user_id: str, transaction_id: str, window_seconds: int = 60, max_tx: int = 5) -> bool:
    """
    detects if a user performs too many transctions
    in a short time frame (window).

    uses redis sorted sets:
    - key: user:{user_id}:recent_txs
    - score: timestamp
    - member: transaction_id
    """

    key = f"user:{user_id}:recent_txs"
    now = time.time()

    pipe = redis_client.pipeline()

    # queue commands
    pipe.zadd(key, {transaction_id: now})
    pipe.zremrangebyscore(key, 0, now - window_seconds)
    pipe.zcard(key)
    pipe.expire(key, window_seconds)

    # count remaining tranactions
    _, _, tx_count, _ = pipe.execute()

    # return anomaly
    return tx_count > max_tx


# =================================
# NEW DEVICE CHECK
# =================================
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

    # expire in 30 days
    redis_client.expire(key, 60 * 60 * 24 * 30)

    return is_new


# =========================
# GEO ANOMALY CHECK
# =========================
def check_geo_anomaly(user_id: str, location: str, time_threshold: int = 3600) -> bool:
    """
    detects suspicious location changes in a short time.

    uses Redis:
    - user:{user_id}:last_location
    - user:{user_id}:last_tx_time
    """

    loc_key = f"user:{user_id}:last_location"
    time_key = f"user:{user_id}:last_tx_time"

    last_location = redis_client.get(loc_key)
    last_time = redis_client.get(time_key)

    now = time.time()
    anomaly = False

    if last_location is not None and last_time is not None:
        last_time = float(last_time)

        if location != last_location and (now - last_time < time_threshold):
            anomaly = True

    # update state and expire
    redis_client.setex(loc_key, time_threshold, location)
    redis_client.setex(time_key, time_threshold, now)

    return anomaly



# =============================
# COOLDOWN SIGNAL
# =============================
def check_cooldown(user_id: str, cooldown_seconds: int = 10) -> bool:
    """
    Prevents rapid repeated actions (rate limiting).
    If user acts too quickly -> flagged.
    """

    key = f"user:{user_id}:cooldown"

    if redis_client.exists(key):
        return True
    
    redis_client.setex(key, cooldown_seconds, 1)

    return False

# =============================
# IP anomaly
# ==============================
def check_ip_anomaly(user_id: str, ip: str) -> bool:
    key = f"user:{user_id}:ips"

    is_new = not redis_client.sismember(key, ip)

    redis_client.sadd(key, ip)
    redis_client.expire(key, 60 * 60 * 24 * 7) # 7 days

    return is_new

# ==============================
# RISK COMPUTATION
# ==============================
def compute_risk(user_id: str, device: str, location: str) -> dict:
    score = 0
    reasons = []

    # temporary unique id
    transaction_id = str(uuid.uuid4())

    if check_velocity(user_id, transaction_id):
        score += RISK_WEIGHTS["velocity"]
        reasons.append("high_velocity")

    if check_new_device(user_id, device):
        score += RISK_WEIGHTS["new_device"]
        reasons.append("new_device")

    if check_geo_anomaly(user_id, location):
        score += RISK_WEIGHTS["geo_anomaly"]
        reasons.append("geo_anomaly")

    if check_cooldown(user_id):
        score += RISK_WEIGHTS["cooldown_violation"]
        reasons.append("cooldown_violation")

    if check_ip_anomaly(user_id, ip):
        score += RISK_WEIGHTS["new_ip"]
        reasons.append("new_ip")


    result = {
        "risk_score": score,
        "reasons": reasons,
        "is_suspicious": score >= SUSPICIOUS_THRESHOLD
    }
    
    print(f"[RISK] user={user_id}, score={score}, reasons={reasons}")

    return result



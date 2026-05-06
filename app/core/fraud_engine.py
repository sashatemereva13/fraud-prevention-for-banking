from app.models.transactions import TransactionCreate
from app.core.graph_checks import run_all_checks
from app.core.risk_scoring import compute_risk_score, decide
from app.services.redis_behavior_service import compute_risk
import logging
from app.db.mongo import transactions_collection

logger = logging.getLogger(__name__)

async def evaluate(txn: TransactionCreate):
    """full evaluation"""
    txn.graph_signals= await run_all_checks(
        account_id=txn.sender.account_id,
        user_id=txn.sender.user_id,
        device_fingerprint=txn.device.device_id,
        ip_address=txn.device.ip_address
    )

    # get mongodb / redis sub-scores (put logic here)
    mongo_score = await _get_mongo_score(txn)
    redis_score = _get_redis_score(txn)

    txn.risk_score = compute_risk_score(txn, mongo_score, redis_score)

    txn.decision = decide(txn.risk_score)

    logger.info(
        "Fraud evaluation | txn=%s score=%.4f decision=%s ring=%s",
        txn.id, txn.risk_score, txn.decision.value, txn.graph_signals.ring_detected,
    )
    return txn


async def _get_mongo_score(txn: TransactionCreate) -> float:
    try:
        score = 0.0

        # Signal 1 — Previous suspicious activity
        previous_fraud = transactions_collection.count_documents({
            "sender.user_id": txn.sender.user_id,
            "decision": {
                "$in": ["review", "block"]
            }
        })

        if previous_fraud >= 3:
            score += 0.40

        elif previous_fraud >= 1:
            score += 0.20

        # Signal 2 — Amount anomaly vs user history
        history_cursor = transactions_collection.find(
            {"sender.user_id": txn.sender.user_id},
            {"amount": 1, "_id": 0}
        ).limit(50)

        history = list(history_cursor)

        if history:

            avg_amount = (
                sum(h["amount"] for h in history)
                / len(history)
            )

            # 5x larger than normal behavior
            if txn.amount > avg_amount * 5:
                score += 0.30

            # 3x larger than normal behavior
            elif txn.amount > avg_amount * 3:
                score += 0.15

        logger.info(
            "Mongo score | user=%s score=%.2f previous_flags=%s",
            txn.sender.user_id,
            score,
            previous_fraud,
        )

        return round(min(score, 1.0), 4)

    except Exception as e:

        logger.warning(
            "Mongo score failed: %s",
            e
        )

        return 0.0


async def _get_redis_score(txn: TransactionCreate):
    # TODO: check rate-limit counters from Redis
    result = compute_risk(
        txn.sender.user_id,
        txn.device.device_id,
        f"{txn.location.country}:{txn.location.city}",
        txn.device.ip_address
    )

    # normalise
    return min(result["risk_score"] / 140, 1.0)

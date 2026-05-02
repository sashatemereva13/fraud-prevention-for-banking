from app.models.transactions import TransactionCreate
from app.core.graph_checks import run_all_checks
from app.core.risk_scoring import compute_risk_score, decide
import logging

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
    redis_score = await _get_redis_score(txn)

    txn.risk_score = compute_risk_score(txn, mongo_score, redis_score)

    txn.decision = decide(txn.risk_score)

    logger.info(
        "Fraud evaluation | txn=%s score=%.4f decision=%s ring=%s",
        txn.id, txn.risk_score, txn.decision, txn.graph_signals.ring_detected,
    )
    return txn


async def _get_mongo_score(txn: TransactionCreate):
    # TODO: query transaction history, flag velocity, blacklisted accounts
    return 0.0


async def _get_redis_score(txn: TransactionCreate):
    # TODO: check rate-limit counters from Redis
    return 0.0

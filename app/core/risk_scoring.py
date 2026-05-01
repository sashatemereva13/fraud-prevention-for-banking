from app.models.transactions import TransactionCreate, GraphSignals, FraudDecision
from app.config import get_settings

settings = get_settings()

def score_graph_signals(signals: GraphSignals):
    """convert GrpahSignals into 0.0-1.0 subscore"""
    score = 0.0
    if signals.ring_detected:
        hop_weight = 1.0/max(signals.ring_hop_count, 1)
        score += 0.45 * hop_weight

    if signals.shared_device_users > settings.GRAPH_DEVICE_SHARE_LIMIT:
        excess = signals.shared_device_users - settings.GRAPH_DEVICE_SHARE_LIMIT
        score += min(0.25, 0.05 * excess)

    if signals.shared_ip_users > 5:
        score += 0.15

    if signals.rapid_forward_chain:
        score+=0.30
    if signals.trust_links==0:
        score+=0.10

    return min(score, 1.0)

def compute_risk_score(txn: TransactionCreate, mongo_score= 0.0, redis_score=0.0):
    """weighted combination of all three databases. and adjust based on false postive tuning."""
    graph_score = score_graph_signals(txn.graph_signals)
    final = (graph_score*0.50+mongo_score*0.35+redis_score*0.15)
    return round(min(final, 1.0),4)

def decide(risk_score):
    if risk_score >= settings.RISK_SCORE_BLOCK_THRESHOLD:
        return FraudDecision.BLOCK
    if risk_score >= settings.RISK_SCORE_ALERT_THRESHOLD:
        return FraudDecision.REVIEW
    return FraudDecision.ALLOW
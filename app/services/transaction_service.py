from datetime import datetime, timezone
from app.core.fraud_engine import evaluate
from app.services.ingestion_service import ingest_transaction_to_graph
from app.models.transactions import TransactionCreate, FraudDecision
from app.db.mongo import (
    transactions_collection,
    alerts_collection
)

# CREATE TRANSACTION
async def create_transaction(data):
    txn = await evaluate(data)

    result = transactions_collection.insert_one(
        txn.model_dump(mode="json")
    )
    await ingest_transaction_to_graph(txn)

    if txn.amount > 10000:
        alert = {
            "transaction_id": txn.id,
            "reason": "High transaction amount",
            "severity": "high",
            "created_at": datetime.now(timezone.utc)
        }

        alerts_collection.insert_one(alert)

    if txn.decision != FraudDecision.ALLOW:
        alerts_collection.insert_one({
            "transaction_id": txn.id,
            "reason": f"Fraud decision: {txn.decision.value}",
            "severity": "high" if txn.decision == FraudDecision.BLOCK else "medium",
            "created_at": datetime.now(timezone.utc)
        })

    return {
        "message": "Transaction created successfully",
        "transaction_id": str(result.inserted_id),
        "external_id": txn.id,
        "risk_score": txn.risk_score,
        "decision": txn.decision.value,
        "graph_signals": txn.graph_signals.model_dump()
    }


# AGGREGATION 1
# Suspicious Transaction Frequency
def suspicious_transaction_frequency():

    pipeline = [
        {
            "$group": {
                "_id": "$sender.user_id",
                "transaction_count": {"$sum": 1}
            }
        },
        {
            "$match": {
                "transaction_count": {"$gt": 5}
            }
        }
    ]

    return list(
        transactions_collection.aggregate(pipeline)
    )


# AGGREGATION 2
# Daily Spending Analysis
def daily_spending_analysis():

    pipeline = [
        {
            "$group": {
                "_id": {
                    "user_id": "$sender.user_id",
                    "date": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$timestamp"
                        }
                    }
                },

                "total_amount": {
                    "$sum": "$amount"
                },

                "transaction_count": {
                    "$sum": 1
                }
            }
        },

        {
            "$sort": {
                "total_amount": -1
            }
        }
    ]

    return list(
        transactions_collection.aggregate(pipeline)
    )
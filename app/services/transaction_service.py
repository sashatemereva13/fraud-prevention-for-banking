from datetime import datetime, timezone

from app.db.mongo import (
    transactions_collection,
    alerts_collection
)

# CREATE TRANSACTION
def create_transaction(data):
    transaction = {
        "sender": data["sender"],
        "receiver": data["receiver"],
        "amount": data["amount"],
        "currency": data["currency"],
        "device": data["device"],
        "location": data["location"],
        "status": data.get("status", "approved"),
        "timestamp": data.get(
            "timestamp",
            datetime.now(timezone.utc)
        )
    }

    result = transactions_collection.insert_one(transaction)

    if transaction["amount"] > 10000:
        alert = {
            "transaction_id": str(result.inserted_id),
            "reason": "High transaction amount",
            "severity": "high",
            "created_at": datetime.now(timezone.utc)
        }

        alerts_collection.insert_one(alert)

    return {
        "message": "Transaction created successfully",
        "transaction_id": str(result.inserted_id)
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
from datetime import datetime, timezone, timedelta

from app.db.mongo import transactions_collection
from app.models.transactions import Transaction


# CREATE TRANSACTION
def create_transaction(data):
    transaction = Transaction(
        user_id=data["user_id"],
        amount=data["amount"],
        location=data["location"],
        device_id=data["device_id"]
    )

    result = transactions_collection.insert_one(transaction.to_dict())

    return {
        "message": "Transaction created successfully",
        "transaction_id": str(result.inserted_id)
    }


# AGGREGATION 1:
# Suspicious transaction frequency
def suspicious_transaction_frequency():
    one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)

    pipeline = [
        {
            "$match": {
                "timestamp": {"$gte": one_minute_ago}
            }
        },
        {
            "$group": {
                "_id": "$user_id",
                "transaction_count": {"$sum": 1}
            }
        },
        {
            "$match": {
                "transaction_count": {"$gt": 5}
            }
        }
    ]

    return list(transactions_collection.aggregate(pipeline))


# AGGREGATION 2:
# Daily spending analysis
def daily_spending_analysis():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "user_id": "$user_id",
                    "date": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$timestamp"
                        }
                    }
                },
                "total_amount": {"$sum": "$amount"},
                "transaction_count": {"$sum": 1}
            }
        },
        {
            "$sort": {"total_amount": -1}
        }
    ]

    return list(transactions_collection.aggregate(pipeline))


# Get user history
def get_user_transactions(user_id):
    return list(
        transactions_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        )
    )
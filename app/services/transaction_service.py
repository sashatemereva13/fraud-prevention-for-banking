from datetime import datetime, timezone, timedelta

from app.db.mongo import transactions_collection


def create_transaction(data):
    transaction = {
        "user_id": data["user_id"],
        "amount": data["amount"],
        "location": data["location"],
        "device_id": data["device_id"],
        "timestamp": datetime.now(timezone.utc),
        "is_fraud": False
    }

    result = transactions_collection.insert_one(transaction)

    return {
        "message": "Transaction created successfully",
        "transaction_id": str(result.inserted_id)
    }


def suspicious_transaction_frequency():
    one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)

    pipeline = [
        {
            "$match": {
                "timestamp": {
                    "$gte": one_minute_ago
                }
            }
        },
        {
            "$group": {
                "_id": "$user_id",
                "transaction_count": {
                    "$sum": 1
                }
            }
        },
        {
            "$match": {
                "transaction_count": {
                    "$gt": 5
                }
            }
        }
    ]

    return list(transactions_collection.aggregate(pipeline))
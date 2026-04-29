from datetime import datetime, timezone, timedelta

from app.db.mongo import transactions_collection


# 1. CREATE TRANSACTION
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


# 2. FRAUD: HIGH FREQUENCY
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



# 3. ANALYTICS: DAILY SPENDING
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
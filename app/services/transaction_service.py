from datetime import datetime, timezone

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
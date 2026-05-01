import random
from datetime import datetime, timezone

from app.db.mongo import transactions_collection


transactions_collection.delete_many({})

sample_transactions = []

for _ in range(100):

    transaction = {
        "sender": {
            "account_id": f"acc_{random.randint(1,5)}",
            "user_id": f"user_{random.randint(1,5)}",
            "username": f"sender_{random.randint(1,5)}"
        },

        "receiver": {
            "account_id": f"acc_{random.randint(6,10)}",
            "user_id": f"user_{random.randint(6,10)}",
            "username": f"receiver_{random.randint(6,10)}"
        },

        "amount": random.randint(100, 5000),

        "currency": "EUR",

        "device": {
            "device_id": f"device_{random.randint(1,20)}",
            "ip_address": f"192.168.1.{random.randint(1,255)}"
        },

        "location": {
            "country": "France",
            "city": "Paris"
        },

        "status": random.choice([
            "approved",
            "flagged",
            "blocked"
        ]),

        "timestamp": datetime.now(timezone.utc)
    }

    sample_transactions.append(transaction)

transactions_collection.insert_many(sample_transactions)

print("100 sample transactions inserted successfully.")
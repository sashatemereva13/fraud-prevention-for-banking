from datetime import datetime, timezone, timedelta
import random

from app.db.mongo import transactions_collection

users = [
    "user_1",
    "user_2",
    "user_3",
    "user_4",
    "user_5"
]

locations = [
    "Paris",
    "London",
    "Berlin",
    "Madrid",
    "Rome"
]

devices = [
    "iphone_15",
    "samsung_s24",
    "macbook_pro",
    "ipad_air",
    "windows_pc"
]

transactions = []

for _ in range(100):
    transaction = {
        "user_id": random.choice(users),
        "amount": random.randint(10, 5000),
        "location": random.choice(locations),
        "device_id": random.choice(devices),
        "timestamp": datetime.now(timezone.utc)
        - timedelta(minutes=random.randint(0, 1440)),
        "is_fraud": random.choice([True, False])
    }

    transactions.append(transaction)

transactions_collection.insert_many(transactions)

print("100 sample transactions inserted successfully.")
"""
Full live integration demo for the fraud pipeline.

Run while the docker-compose stack and API are up:

    python scripts/test_full_pipeline.py

This script demonstrates that one transaction evaluation combines:
  - Neo4j graph signals
  - MongoDB transaction history
  - Redis real-time behavior
"""

import asyncio
from datetime import datetime, timedelta, timezone
import sys

import requests

sys.path.append(".")

from app.db.mongo import transactions_collection, alerts_collection
from app.db.redis_client import redis_client
from scripts.test_live import API, seed_neo4j


TEST_USERS = {
    "mongo": "user-mongo-history-001",
    "combined": "user-combined-001",
    "clean": "user-clean-001",
}


def cleanup_demo_data():
    """Remove only records created by this demo script."""
    user_ids = list(TEST_USERS.values())

    transactions_collection.delete_many(
        {
            "$or": [
                {"sender.user_id": {"$in": user_ids}},
                {"id": {"$regex": "^pipeline-demo-"}},
            ]
        }
    )
    alerts_collection.delete_many(
        {"transaction_id": {"$regex": "^pipeline-demo-"}}
    )

    for user_id in user_ids:
        for key in redis_client.scan_iter(f"user:{user_id}:*"):
            redis_client.delete(key)


def seed_mongo_history():
    """Create MongoDB history that the fraud engine can score."""
    now = datetime.now(timezone.utc)

    normal_history = []
    for i in range(6):
        normal_history.append(
            {
                "id": f"pipeline-demo-normal-{i}",
                "sender": {
                    "account_id": "acc-mongo-history-001",
                    "user_id": TEST_USERS["mongo"],
                    "username": "mongo_history_user",
                },
                "receiver": {
                    "account_id": f"acc-mongo-history-recv-{i}",
                    "user_id": f"user-mongo-history-recv-{i}",
                    "username": "receiver",
                },
                "amount": 100.0,
                "currency": "USD",
                "device": {
                    "device_id": "device-mongo-history-001",
                    "ip_address": "203.0.113.10",
                },
                "location": {"country": "US", "city": "Boston"},
                "status": "approved",
                "timestamp": now - timedelta(days=i + 1),
                "risk_score": 0.05,
                "decision": "allow",
                "graph_signals": {},
            }
        )

    previous_flags = []
    for i in range(3):
        previous_flags.append(
            {
                **normal_history[0],
                "id": f"pipeline-demo-flagged-{i}",
                "amount": 250.0,
                "timestamp": now - timedelta(hours=i + 1),
                "risk_score": 0.8,
                "decision": "review",
            }
        )

    transactions_collection.insert_many(normal_history + previous_flags)
    print("  MongoDB seeded with normal history and previous reviewed transactions")


def post_transaction(label, payload):
    print(f"\n{'-' * 58}")
    print(label)
    print(f"{'-' * 58}")

    response = requests.post(f"{API}/transactions", json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()

    print(f"Decision:      {data['decision']}")
    print(f"Risk score:    {data['risk_score']}")
    print(f"Transaction:   {data['external_id']}")
    print("Graph signals:")
    for key, value in data["graph_signals"].items():
        print(f"  {key}: {value}")

    return data


def transaction_payload(user_id, account_id, amount, device_id, ip_address, city):
    return {
        "id": f"pipeline-demo-{user_id}-{int(datetime.now().timestamp())}",
        "sender": {
            "account_id": account_id,
            "user_id": user_id,
            "username": user_id.replace("-", "_"),
        },
        "receiver": {
            "account_id": f"{account_id}-receiver",
            "user_id": f"{user_id}-receiver",
            "username": "receiver",
        },
        "amount": amount,
        "currency": "USD",
        "device": {"device_id": device_id, "ip_address": ip_address},
        "location": {"country": "US", "city": city},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def run_pipeline_demo():
    print("\n=== Cleaning previous demo data ===")
    cleanup_demo_data()

    print("\n=== Seeding MongoDB history ===")
    seed_mongo_history()

    print("\n=== MongoDB history anomaly ===")
    post_transaction(
        "Mongo test: previous reviews + amount much larger than user average",
        transaction_payload(
            TEST_USERS["mongo"],
            "acc-mongo-history-001",
            1200.0,
            "device-mongo-history-001",
            "203.0.113.10",
            "Boston",
        ),
    )

    print("\n=== Redis velocity anomaly ===")
    for i in range(6):
        result = post_transaction(
            f"Redis test: rapid transaction {i + 1}/6",
            transaction_payload(
                "user-velocity-001",
                "acc-velocity-001",
                100.0,
                "device-velocity-001",
                "192.168.5.5",
                "Dallas",
            ),
        )
        if result["decision"] in {"review", "block"}:
            print("Redis velocity/cooldown behavior triggered a fraud decision")
            break

    print("\n=== Neo4j graph anomaly ===")
    post_transaction(
        "Neo4j test: sender account belongs to seeded circular transfer ring",
        transaction_payload(
            "user-ring-sender",
            "acc-ring-A",
            1000.0,
            "device-ring-001",
            "192.168.1.10",
            "Chicago",
        ),
    )

    print("\n=== Clean control transaction ===")
    post_transaction(
        "Control test: trusted clean user with normal transaction",
        transaction_payload(
            TEST_USERS["clean"],
            "acc-clean-001",
            150.0,
            "device-clean-unique-999",
            "10.10.10.10",
            "New York",
        ),
    )


if __name__ == "__main__":
    print("=== Seeding Neo4j graph patterns ===")
    asyncio.run(seed_neo4j())
    run_pipeline_demo()

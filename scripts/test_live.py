"""
Manual end-to-end test script.
Run this while your docker-compose stack is up.

    python scripts/test_live.py

It will:
  1. Seed Neo4j with fraud patterns
  2. Hit the API with transactions that SHOULD trigger fraud
  3. Hit the API with a clean transaction that SHOULD pass
  4. Print the results clearly so you can see fraud messages
"""

import asyncio
import requests
from datetime import datetime, timezone

API = "http://localhost:8000"


# ─────────────────────────────────────────────────────────
# STEP 1 — Seed Neo4j with fraud patterns
# ─────────────────────────────────────────────────────────


async def seed_neo4j():
    """
    Creates the graph data that fraud checks will find.
    Must run before the API tests below.
    """
    import sys

    sys.path.append(".")
    from app.db.neo4j_client import neo4j_client

    await neo4j_client.connect()

    print("\n── Seeding Neo4j ─────────────────────────────────")

    account_ids = [
        "acc-ring-A", "acc-ring-B", "acc-ring-C",
        "acc-shared-sender", "acc-shared-recv",
        "acc-ip-sender", "acc-ip-recv",
        "acc-synth-001", "acc-synth-recv",
        "acc-velocity-001", *[f"acc-velocity-recv-{i}" for i in range(6)],
        "acc-clean-001", "acc-clean-recv",
    ]
    user_ids = [
        *[f"fraud-user-{i}" for i in range(5)],
        *[f"ip-user-{i}" for i in range(6)],
        *[f"trusted-user-{i}" for i in range(3)],
        "user-ring-sender", "user-ring-recv",
        "user-shared-new", "user-shared-recv",
        "user-ip-new", "user-ip-recv",
        "user-synth-001", "user-synth-recv",
        "user-velocity-001", *[f"user-velocity-recv-{i}" for i in range(6)],
        "user-clean-001", "user-clean-recv",
    ]
    device_ids = [
        "SHARED-DEVICE-001",
        "device-ring-001",
        "device-ip-001",
        "device-synth-001",
        "device-velocity-001",
        "device-clean-unique-999",
    ]
    ip_addresses = [
        "192.168.1.10",
        "192.168.1.20",
        "10.0.0.99",
        "172.16.0.1",
        "192.168.5.5",
        "10.10.10.10",
    ]

    await neo4j_client.run_write(
        """
        MATCH (n)
        WHERE
          (n:Account AND n.id IN $account_ids)
          OR (n:User AND n.id IN $user_ids)
          OR (n:Device AND n.fingerprint IN $device_ids)
          OR (n:IpAddress AND n.address IN $ip_addresses)
        DETACH DELETE n
        """,
        {
            "account_ids": account_ids,
            "user_ids": user_ids,
            "device_ids": device_ids,
            "ip_addresses": ip_addresses,
        },
    )

    # --- Pattern 1: Circular ring (acc-A → acc-B → acc-C → acc-A) ---
    # When user-ring-sender sends from acc-ring-A, this ring will be detected
    for acc_id in ["acc-ring-A", "acc-ring-B", "acc-ring-C"]:
        await neo4j_client.run_write("MERGE (a:Account {id: $id})", {"id": acc_id})

    import time

    now_ms = int(time.time() * 1000)
    ring_transfers = [
        ("acc-ring-A", "acc-ring-B"),
        ("acc-ring-B", "acc-ring-C"),
        ("acc-ring-C", "acc-ring-A"),  # loops back — this is the ring
    ]
    for src, dst in ring_transfers:
        await neo4j_client.run_write(
            """
            MATCH (s:Account {id: $src}), (d:Account {id: $dst})
            CREATE (s)-[:TRANSFERRED_TO {
                txn_id: $txn_id, amount: 1000.0, timestamp: $ts
            }]->(d)
            """,
            {"src": src, "dst": dst, "txn_id": f"seed-{src}-{dst}", "ts": now_ms},
        )
    print("  ✓ Circular ring seeded (acc-ring-A → B → C → A)")

    # --- Pattern 2: Shared device (5 users on one device) ---
    await neo4j_client.run_write(
        "MERGE (d:Device {fingerprint: $fp})", {"fp": "SHARED-DEVICE-001"}
    )
    for i in range(5):
        await neo4j_client.run_write(
            """
            MERGE (u:User {id: $uid})
              ON CREATE SET u.verified = false, u.risk_score = 0.0,
                            u.created_at = timestamp()
            MERGE (d:Device {fingerprint: $fp})
            MERGE (u)-[:USES]->(d)
            """,
            {"uid": f"fraud-user-{i}", "fp": "SHARED-DEVICE-001"},
        )
    print("  ✓ Shared device seeded (5 users on SHARED-DEVICE-001)")

    # --- Pattern 3: Shared IP (6 users on same IP in last 24h) ---
    await neo4j_client.run_write(
        "MERGE (ip:IpAddress {address: $ip})", {"ip": "10.0.0.99"}
    )
    for i in range(6):
        await neo4j_client.run_write(
            """
            MERGE (u:User {id: $uid})
              ON CREATE SET u.verified = false, u.risk_score = 0.0,
                            u.created_at = timestamp()
            MERGE (ip:IpAddress {address: $ip})
            CREATE (u)-[:LOGGED_IN_FROM {timestamp: timestamp()}]->(ip)
            """,
            {"uid": f"ip-user-{i}", "ip": "10.0.0.99"},
        )
    print("  ✓ Shared IP seeded (6 users on 10.0.0.99)")

    # --- Clean user — has verified connections ---
    await neo4j_client.run_write(
        """
        MERGE (u:User {id: 'user-clean-001'})
          ON CREATE SET u.verified = true, u.risk_score = 0.0,
                        u.created_at = timestamp() - 2592000000
        MERGE (a:Account {id: 'acc-clean-001'})
        MERGE (u)-[:OWNS]->(a)
        """,
        {},
    )
    # Give them trusted connections
    for i in range(3):
        await neo4j_client.run_write(
            """
            MERGE (trusted:User {id: $tid})
              SET trusted.verified = true
            MERGE (clean:User {id: 'user-clean-001'})
            MERGE (clean)-[:TRANSFERRED_TO]->(trusted)
            """,
            {"tid": f"trusted-user-{i}"},
        )
    print("  ✓ Clean user seeded (user-clean-001 with trusted connections)")

    await neo4j_client.close()
    print("── Seeding complete ──────────────────────────────\n")


# ─────────────────────────────────────────────────────────
# STEP 2 — API test transactions
# ─────────────────────────────────────────────────────────


def post_transaction(label, payload):
    """Hit the API and print the result clearly."""
    print(f"\n{'─'*50}")
    print(f"TEST: {label}")
    print(f"{'─'*50}")

    try:
        resp = requests.post(f"{API}/transactions", json=payload, timeout=10)
        data = resp.json()

        decision = data.get("decision", "unknown").upper()
        score = data.get("risk_score", 0)
        signals = data.get("graph_signals", {})

        # colour coding in terminal
        if decision == "BLOCK":
            tag = "🔴 BLOCKED"
        elif decision == "REVIEW":
            tag = "🟡 REVIEW"
        else:
            tag = "🟢 ALLOWED"

        print(f"  Decision:   {tag}")
        print(f"  Risk score: {score}")
        print(f"  Txn ID:     {data.get('external_id', '-')}")
        print(f"\n  Graph signals:")
        print(f"    Ring detected:       {signals.get('ring_detected')}")
        print(f"    Ring hop count:      {signals.get('ring_hop_count')}")
        print(f"    Shared device users: {signals.get('shared_device_users')}")
        print(f"    Shared IP users:     {signals.get('shared_ip_users')}")
        print(f"    Rapid forward chain: {signals.get('rapid_forward_chain')}")
        print(f"    Trust links:         {signals.get('trust_links')}")

        return data

    except requests.exceptions.ConnectionError:
        print("  ❌ Could not connect — is docker-compose running?")
        return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def run_api_tests():
    print("\n\n══════════════════════════════════════════════════")
    print("  FRAUD DETECTION — LIVE API TESTS")
    print("══════════════════════════════════════════════════")

    # ── TEST 1: Circular ring transaction ────────────────
    # Sender account is acc-ring-A which is inside a seeded ring
    post_transaction(
        "Circular ring — sender is part of A→B→C→A ring",
        {
            "sender": {
                "account_id": "acc-ring-A",
                "user_id": "user-ring-sender",
                "username": "ring_user",
            },
            "receiver": {
                "account_id": "acc-ring-B",
                "user_id": "user-ring-recv",
                "username": "ring_recv",
            },
            "amount": 1000.0,
            "currency": "USD",
            "device": {"device_id": "device-ring-001", "ip_address": "192.168.1.10"},
            "location": {"country": "US", "city": "Chicago"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    # ── TEST 2: Shared device fraud ──────────────────────
    # Uses SHARED-DEVICE-001 which already has 5 users on it
    post_transaction(
        "Shared device — device already used by 5 other accounts",
        {
            "sender": {
                "account_id": "acc-shared-sender",
                "user_id": "user-shared-new",
                "username": "shared_user",
            },
            "receiver": {
                "account_id": "acc-shared-recv",
                "user_id": "user-shared-recv",
                "username": "shared_recv",
            },
            "amount": 750.0,
            "currency": "USD",
            "device": {"device_id": "SHARED-DEVICE-001", "ip_address": "192.168.1.20"},
            "location": {"country": "US", "city": "Miami"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    # ── TEST 3: Shared IP fraud ──────────────────────────
    # Uses 10.0.0.99 which already has 6 users logged in from it
    post_transaction(
        "Shared IP — IP already used by 6 users in last 24h",
        {
            "sender": {
                "account_id": "acc-ip-sender",
                "user_id": "user-ip-new",
                "username": "ip_user",
            },
            "receiver": {
                "account_id": "acc-ip-recv",
                "user_id": "user-ip-recv",
                "username": "ip_recv",
            },
            "amount": 300.0,
            "currency": "USD",
            "device": {"device_id": "device-ip-001", "ip_address": "10.0.0.99"},
            "location": {"country": "US", "city": "Houston"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    # ── TEST 4: High amount + no trust network ───────────
    # Brand new user, no connections, very high amount
    post_transaction(
        "Synthetic identity — new user, no trust links, high amount",
        {
            "sender": {
                "account_id": "acc-synth-001",
                "user_id": "user-synth-001",
                "username": "newuser",
            },
            "receiver": {
                "account_id": "acc-synth-recv",
                "user_id": "user-synth-recv",
                "username": "recv",
            },
            "amount": 15000.0,
            "currency": "USD",
            "device": {"device_id": "device-synth-001", "ip_address": "172.16.0.1"},
            "location": {"country": "US", "city": "Seattle"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    # ── TEST 5: Velocity test — same user, rapid fire ────
    # Send 6 transactions quickly to trigger Redis velocity flag
    print(f"\n{'─'*50}")
    print("TEST: Velocity — 6 rapid transactions from same user")
    print(f"{'─'*50}")
    for i in range(6):
        result = post_transaction(
            f"  Rapid fire #{i+1}",
            {
                "sender": {
                    "account_id": "acc-velocity-001",
                    "user_id": "user-velocity-001",
                    "username": "speeduser",
                },
                "receiver": {
                    "account_id": f"acc-velocity-recv-{i}",
                    "user_id": f"user-velocity-recv-{i}",
                    "username": "recv",
                },
                "amount": 100.0,
                "currency": "USD",
                "device": {
                    "device_id": "device-velocity-001",
                    "ip_address": "192.168.5.5",
                },
                "location": {"country": "US", "city": "Dallas"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        if result and result.get("decision") in ("review", "block"):
            print(f"\n  ⚡ Velocity flagged on transaction #{i+1}")
            break

    # ── TEST 6: Clean transaction ─────────────────────────
    # Known clean user with trusted connections, normal amount
    post_transaction(
        "Clean transaction — verified user, normal amount, unique device",
        {
            "sender": {
                "account_id": "acc-clean-001",
                "user_id": "user-clean-001",
                "username": "alice",
            },
            "receiver": {
                "account_id": "acc-clean-recv",
                "user_id": "user-clean-recv",
                "username": "bob",
            },
            "amount": 150.0,
            "currency": "USD",
            "device": {
                "device_id": "device-clean-unique-999",
                "ip_address": "10.10.10.10",
            },
            "location": {"country": "US", "city": "New York"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    print(f"\n\n══════════════════════════════════════════════════")
    print("  Done. Check your alerts collection for flagged txns:")
    print("  GET http://localhost:8000/alerts")
    print("══════════════════════════════════════════════════\n")


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Step 1 — seeding Neo4j with fraud patterns...")
    asyncio.run(seed_neo4j())

    print("Step 2 — running API tests...")
    run_api_tests()

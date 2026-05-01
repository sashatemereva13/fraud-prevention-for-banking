import asyncio, uuid
from app.db.neo4j_client import neo4j_client
# 20 users with unique account ids and unique devices
async def seed():
    await neo4j_client.connect()
    for u in range(20):
        user_id = str(uuid.uuid4())
        acct_id = str(uuid.uuid4())
        device_fp = str(uuid.uuid4())

        await neo4j_client.run_write(
            """merge (u: User {id: $uid})
            set u.verified = true, u.risk_score=0.0,
            u.created_at = timestamp() - $age_ms
            merge (a:Account {id: $aid})
            merge (d:Device {fingerprint: $fp})
            merge (u)-[:OWNS]-(a)
            merge (u)-[:USES]-(d)""", 
            {"uid":user_id, "aid": acct_id, "fp":device_fp,
             "age_ms": (u+1) * 86_400_000} #ms in one day so accounts aged 1-20 days.
        )

    # fraud cluster: 5 accs sharing one device.

    shared_device="FRAUD-DEVICE-001"
    await neo4j_client.run_write("merge (d:Device {fingerprint: $fp})", {"fp": shared_device})
    for _ in range(5):
        user_id = str(uuid.uuid4())
        await neo4j_client.run_write(
            """merge (u:User {id: $uid})
                                     set u.verified = false, u.risk_score=0.0, 
                                     u.created_at= timestamp()
                                     merge (d:Device {fingerprint: $fp})
                                     merge (u)-[:USES]-(d)""",
            {"uid": user_id, "fp": shared_device},
        )
    print("20 seeded user + 5-account fraud clusters.")
    await neo4j_client.close()
asyncio.run(seed())

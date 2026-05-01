# creates a 4-hop circular ring
import asyncio, uuid, time
from app.db.neo4j_client import neo4j_client


async def create_ring(hop_count=4):
    account_ids = [str(uuid.uuid4()) for _ in range(hop_count)]

    for acc_id in account_ids:
        await neo4j_client.run_write("Merge (a:Account {id: $id})", {"id": acc_id})

    now_ms = int(time.time() * 1000)

    for i in range(hop_count):
        src = account_ids[i]
        dst = account_ids[(i + 1) % hop_count]

        await neo4j_client.run_write(
            """match (s:Account {id:$src}), (d:Account {id:$dst})
                                     create (s)-[:TRANSFERRED_TO 
                                    {txn_id:$txn_id, amount:100.0, timestamp:$ts}]-(d)""",
            {"src": src, "dst": dst, "txn_id": str(uuid.uuid4), "ts": now_ms}
        )
    print("Created {hop_count}-hop ring. Start account: {account_ids[0]}")
    return account_ids[0]

# creates a 5 step forwarding chain
async def create_rapid_chain(steps=5):
    account_ids = [str(uuid.uuid4()) for _ in range(steps+1)]
    now_ms = int(time.time()*1000)

    for acc_id in account_ids:
        await neo4j_client.run_write("Merge (a:Account {id: $id})", {"id": acc_id})
    for i in range(steps):
        await neo4j_client.run_write(
            """match (s:Account {id:$src}), (d:Account {id:$dst})
                                     create (s)-[:TRANSFERRED_TO 
                                    {txn_id:$txn_id, amount:500.0, timestamp:$ts}]-(d)""",
            {"src": account_ids[i], "dst": account_ids[i+1], "txn_id": str(uuid.uuid4), "ts": now_ms+i*60_000},
        )
    print("CCreated {steps}-step rapid chain. Destination: {account_ids[-1]}")
    return account_ids[-1]

async def main():
    await neo4j_client.connect()
    ring_start = await create_ring(4)
    chain_end = await create_rapid_chain(5)
    print(f"\nTest ring check:    GET /transactions/graph/ring/{ring_start}")
    print(f"Test forward check: account_id={chain_end} via /transactions")
    await neo4j_client.close()

asyncio.run(main())
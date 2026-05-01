from app.db.neo4j_client import neo4j_client
from app.models.transactions import TransactionCreate
import logging

logger = logging.getLogger(__name__)

async def ingest_transaction_to_graph(txn:TransactionCreate):
    # ensure User and Account node exist
    await neo4j_client.run_write(
        """merge (u:User {id: $user_id})
        on create set u.risk_score = 0.0, u.verified = false,
                    u.created_at = timestamp()
        merge (sender:Account {id:$sender_id}) merge (receiver:Account {id:$receiver_id})
        merge (u)-[:OWNS]->(sender)""",
        {
            "user_id": txn.sender.user_id,
            "sender_id": txn.sender.account_id,
            "receiver_id": txn.receiver.account_id,
        },
    )
    # write the TRANSFERRED_TO relationship
    await neo4j_client.run_write(
        """match (sender:Account {id:$sender_id})
        match (receiver:Account {id:$receiver_id})
        create (sender)-[:TRANSFERRED_TO {txn_id: $txn_id,
                                        amount: $amount,
                                        currency: $currency,
                                        timestamp: $ts,
                                        risk_score: $risk_score}]->(receiver)""",
        {
            "sender_id": txn.sender.account_id,
            "receiver_id": txn.receiver.account_id,
            "txn_id": txn.id,
            "amount":txn.amount,
            "currency": txn.currency,
            "ts": int(txn.timestamp.timestamp()*1000),
            "risk_score":txn.risk_score,
        },
    )
    # optionally link device and IP
    if txn.device.device_id:
        await neo4j_client.run_write(
            """match (u:User {id:$user_id})
            merge (d:Device {fingerprint: $fp})
            merge (u)-[:USES]->(d)""",
            {"user_id":txn.sender.user_id, "fp":txn.device.device_id},
        )
    if txn.device.ip_address:
        await neo4j_client.run_write(
            """match (u:User {id:$user_id})
            merge (ip:IpAddress {address: $ip})
            create (u)-[:LOGGED_IN_FROM {timestamp: timestamp()}]->(ip)""",
            {"user_id":txn.sender.user_id, "ip":txn.device.ip_address},
        )
    await neo4j_client.run_write(
        """match (u:User {id: $user_id})
        set u.risk_score = $risk_score""",
        {"user_id": txn.sender.user_id, "risk_score":txn.risk_score},
    )
    logger.debug("Graph ingested txn=%s", txn.id)

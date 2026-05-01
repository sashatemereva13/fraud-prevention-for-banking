from app.db.neo4j_client import neo4j_client
from app.models.transactions import GraphSignals
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


async def check_circular_ring(account_id):
    """Detects money that leaved and returns to the
    same account through a chain of transfers."""
    rows = await neo4j_client.run_query(
        """match path = (a:Account {id:$account_id})
        -[:TRANSFERRED_TO*2..$max_hops]->(a)
        return length(path) as hops order by hops asc
        limit 1""", {"account_id": account_id, "max_hops": settings.GRAPH_RING_MAX_HOPS},
    )
    if rows:
        return {"ring_detected": True, "ring_hop_count": rows[0]["hops"]}
    return {"ring_detected": False, "ring_hop_count": 0}

async def check_device_sharing(device_fingerprint):
    """how many user accs use this device?"""
    if not device_fingerprint:
        return {"shared_device_users":0}
    rows = await neo4j_client.run_query("""match (d:Device {fingerprint:$fp})<-[:USES]-(u:User)
                                        return count(u) as user_count""",
                                        {"fp":device_fingerprint})
    count = rows[0]["user_count"] if rows else 0
    return {"shared_device_users":count}

async def check_ip_sharing(ip_address):
    """how many users have loggen in from this ip?"""
    if not ip_address:
        return {"shared_ip_users":0}
    rows = await neo4j_client.run_query(

        """match (ip:IpAddress {address: $ip})<-[r:LOGGED_IN_FROM]-(u:User)
        where r.timestamp > (timestamp()-86400000)
        return count(distinct u) as user_count""",
        {"ip":ip_address})
    count = rows[0]["user_count"] if rows else 0
    return {"shared_ip_users":count}

async def check_rapid_forwarding(account_id, window_ms=3_600_000):
    """detects funds that move thro +3 accs within 1hr (default)"""
    rows = await neo4j_client.run_query(
        """match path = (src:Account)-[r:TRANSFERRED_TO*3..6]->(dst:Account {id:$account_id})
        where src <> dst
        and all(rel in relationships(path) where rel.timestamp > (timestamp()- $window_ms))
        return length(path) as chain_length
        order by chain_length desc limit 1""",
        {"account_id":account_id, "window_ms":window_ms}
    )
    return {"rapid_forward_chain": bool(rows)}

async def check_trust_network(user_id):
    """how many verified users is this user connected to"""
    rows = await neo4j_client.run_query(
        """match (u:User {id:$user_id})-[*1..2]-(trusted:User {verified: true})
        where u <> trusted
        return count(distinct trusted) as trust_links""",
        {"user_id": user_id}
    )
    count = rows[0]["trust_links"] if rows else 0
    return {"trust_links":count}

async def run_all_checks(account_id, user_id, device_fingerprint, ip_address):
    """runs all graph checks and merges results into a single GraphSignal object"""
    import asyncio
    ring, device, ip, forward, trust = await asyncio.gather(
        check_circular_ring(account_id), 
        check_device_sharing(device_fingerprint),
        check_ip_sharing(ip_address),
        check_rapid_forwarding(account_id),
        check_trust_network(user_id),
        return_exceptions=True
    )
    merged = {}
    for result in (ring, device, ip, forward, trust):
        if isinstance(result, Exception):
            logger.warning("Graph check failed: %s", result)
        else:
            merged.update(result)
    return GraphSignals(**merged)

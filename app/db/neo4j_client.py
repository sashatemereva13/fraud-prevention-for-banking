from neo4j import AsyncGraphDatabase, AsyncDriver
from neo4j.exceptions import ServiceUnavailable, AuthError
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class Neo4jClient:
    _driver = None
    async def connect(self): 
        try:
            self._driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                max_connection_pool_size=settings.NEO4J_MAX_CONNECTION_POOL,
                connection_timeout=settings.NEO4J_CONNECTION_TIMEOUT,
            )
            await self._driver.verify_connectivity()
            logger.info("Neo4j connected %s", settings.NEO4J_URI)
        except AuthError:
            logger.error("Neo4j auth error, check NEO4J_USER or NEO4J_PASSWORD")
            raise
        except ServiceUnavailable:
            logger.error("Neo4j not connected %s", settings.NEO4J_URI)
            raise

    async def close(self):
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j connection closed")

    async def run_query(self, cypher, params = None, *, database = "neo4j"):
        if not self._driver:
            raise RuntimeError("Neo4j is not initialised. Call connect()")
        async with self._driver.session(database=database) as session:
            result = await session.run(cypher, params or {})
            return [record.data() async for record in result]

    async def run_write(self, cypher, params = None):
        """for merge and create that returns nothing, with retry safety."""
        async def _tx(tx):
            await tx.run(cypher, params or {})
        async with self._driver.session() as session:
            await session.execute_write(_tx)

neo4j_client = Neo4jClient()

from neo4j import AsyncGraphDatabase, AsyncDriver
from neo4j.exceptions import ServiceUnavailable, AuthError
import os
from dotenv import load_dotenv
import logging

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_MAX_CONNECTION_POOL = os.getenv("NEO4J_MAX_CONNECTION_POOL")
NEO4J_CONNECTION_TIMEOUT = os.getenv("NEO4J_CONNECTION_TIMEOUT")

logger = logging.getLogger(__name__)

class Neo4jClient:
    _driver = None
    async def connect(self): 
        try:
            self._driver = AsyncGraphDatabase.driver(NEO4J_URI, auth = (NEO4J_USER, NEO4J_PASSWORD),
                                                     max_connection=NEO4J_MAX_CONNECTION_POOL,
                                                     connection_timeout=NEO4J_CONNECTION_TIMEOUT) 
            await self._driver.verify_connectivity()
            logger.info("Neo4j connected %s", NEO4J_URI)
        except AuthError:
            logger.error("Neo4j auth error, check NEO4J_USER or NEO4J_PASSWORD")
            raise
        except ServiceUnavailable:
            logger.error("Neo4j not connected %s", NEO4J_URI)
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


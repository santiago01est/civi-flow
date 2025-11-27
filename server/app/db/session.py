# app/db/session.py

from typing import Optional
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceExistsError
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Module-level client/database that will be initialized explicitly
_client: Optional[CosmosClient] = None
_database = None

# Containers and their partition keys
CONTAINERS = {
    "users": PartitionKey(path="/id"),
    "conversations": PartitionKey(path="/id"),
    "notifications": PartitionKey(path="/id"),
}

def init_cosmos():
    """Initialize Cosmos client and ensure database + containers exist.

    This should be called once at application startup (e.g. in FastAPI lifespan).
    """
    global _client, _database
    if _client is not None:
        return

    if not settings.COSMOS_DB_ENDPOINT or not settings.COSMOS_DB_KEY:
        logger.warning("COSMOS_DB_ENDPOINT or COSMOS_DB_KEY not set — skipping Cosmos initialization.")
        return

    _client = CosmosClient(settings.COSMOS_DB_ENDPOINT, credential=settings.COSMOS_DB_KEY)

    try:
        _database = _client.create_database(settings.COSMOS_DB_DATABASE_NAME)
    except CosmosResourceExistsError:
        _database = _client.get_database_client(settings.COSMOS_DB_DATABASE_NAME)

    for container_name, partition_key in CONTAINERS.items():
        try:
            _database.create_container(id=container_name, partition_key=partition_key)
        except CosmosResourceExistsError:
            pass

    logger.info("Cosmos DB initialized (database=%s)", settings.COSMOS_DB_DATABASE_NAME)

def close_cosmos():
    """Close the Cosmos client if possible and clear references."""
    global _client, _database
    if _client:
        try:
            if hasattr(_client, "close"):
                _client.close()
        except Exception:
            logger.exception("Error while closing Cosmos client")

    _client = None
    _database = None
    logger.info("Cosmos client closed")

def get_db_client() -> Optional[CosmosClient]:
    return _client

def get_database():
    return _database

def get_container(container_name: str):
    if _database is None:
        raise RuntimeError("Cosmos DB not initialized. Call init_cosmos() during app startup.")
    return _database.get_container_client(container_name)

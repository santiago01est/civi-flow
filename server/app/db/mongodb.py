# Azure Cosmos DB (SQL API) connection management
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
from typing import Optional
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class CosmosDB:
    client: Optional[CosmosClient] = None
    database = None
    

cosmosdb = CosmosDB()


async def connect_to_cosmos():
    """Connect to Azure Cosmos DB"""
    try:
        logger.info(f"Connecting to Azure Cosmos DB...")
        
        # Parse connection string
        endpoint = settings.COSMOS_ENDPOINT
        key = settings.COSMOS_KEY
        
        cosmosdb.client = CosmosClient(endpoint, key)
        
        # Get or create database
        cosmosdb.database = cosmosdb.client.get_database_client(settings.COSMOS_DATABASE_NAME)
        
        # Create database if it doesn't exist
        try:
            await cosmosdb.database.read()
            logger.info(f"Connected to existing database: {settings.COSMOS_DATABASE_NAME}")
        except:
            await cosmosdb.client.create_database(settings.COSMOS_DATABASE_NAME)
            cosmosdb.database = cosmosdb.client.get_database_client(settings.COSMOS_DATABASE_NAME)
            logger.info(f"Created new database: {settings.COSMOS_DATABASE_NAME}")
        
        # Create containers (collections) if they don't exist
        await _create_containers()
        
        logger.info("Successfully connected to Azure Cosmos DB")
    except Exception as e:
        logger.error(f"Failed to connect to Cosmos DB: {str(e)}")
        raise


async def _create_containers():
    """Create containers (collections) for the application"""
    containers = [
        {
            "id": "conversations",
            "partition_key": PartitionKey(path="/id"),
        },
        {
            "id": "messages",
            "partition_key": PartitionKey(path="/conversation_id"),
        },
        {
            "id": "notifications",
            "partition_key": PartitionKey(path="/user_id"),
        },
        {
            "id": "users",
            "partition_key": PartitionKey(path="/id"),
        },
    ]
    
    for container_def in containers:
        try:
            container = cosmosdb.database.get_container_client(container_def["id"])
            await container.read()
            logger.info(f"✓ Container '{container_def['id']}' already exists")
        except:
            await cosmosdb.database.create_container(
                id=container_def["id"],
                partition_key=container_def["partition_key"]
            )
            logger.info(f"✓ Created container '{container_def['id']}'")


async def close_cosmos_connection():
    """Close Cosmos DB connection"""
    try:
        if cosmosdb.client:
            await cosmosdb.client.close()
            logger.info("Closed Cosmos DB connection")
    except Exception as e:
        logger.error(f"Error closing Cosmos DB connection: {str(e)}")


def get_database():
    """Get Cosmos DB database instance"""
    if cosmosdb.database is None:
        raise RuntimeError("Cosmos DB client is not initialized")
    return cosmosdb.database


async def get_db():
    """Dependency injection for database"""
    return get_database()


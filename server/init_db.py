#!/usr/bin/env python3
"""
Azure Cosmos DB database initialization script
Creates containers with partition keys
"""
import asyncio
import sys
from pathlib import Path

# Add the server directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.mongodb import connect_to_cosmos, close_cosmos_connection, get_database
from app.config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify_containers():
    """Verify that Cosmos DB containers exist"""
    try:
        await connect_to_cosmos()
        db = get_database()
        
        logger.info("Verifying Cosmos DB containers...")
        
        containers = ["conversations", "messages", "notifications", "users"]
        
        for container_name in containers:
            try:
                container = db.get_container_client(container_name)
                # Try to read container properties to verify it exists
                await container.read()
                logger.info(f"✓ Container '{container_name}' exists")
            except Exception as e:
                logger.warning(f"⚠ Container '{container_name}' not found: {str(e)}")
        
        logger.info("✅ Container verification complete!")
        
        # Display container stats
        logger.info("\n📊 Database Statistics:")
        for container_name in containers:
            try:
                container = db.get_container_client(container_name)
                # Query to count items
                query = "SELECT VALUE COUNT(1) FROM c"
                count = 0
                async for item in container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ):
                    count = item
                    break
                logger.info(f"  - {container_name}: {count} items")
            except Exception as e:
                logger.warning(f"  - {container_name}: Unable to count ({str(e)})")
        
        await close_cosmos_connection()
        
    except Exception as e:
        logger.error(f"❌ Error verifying containers: {str(e)}")
        raise


async def main():
    """Main initialization function"""
    logger.info("=== Azure Cosmos DB Initialization ===")
    logger.info(f"Database: {settings.COSMOS_DATABASE_NAME}")
    logger.info(f"Endpoint: {settings.COSMOS_ENDPOINT}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("")
    
    await verify_containers()
    
    logger.info("\n✅ Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(main())


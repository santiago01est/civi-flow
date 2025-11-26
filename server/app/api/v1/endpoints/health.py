from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import os
import logging
import requests
from app.config.settings import settings


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT
    }


@router.get("/health/detailed", tags=["Health"])
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with all Azure services status
    """
    health_status = {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT,
        "services": {}
    }
    
    # Check Key Vault
    health_status["services"]["key_vault"] = await _check_key_vault()
    
    # Check Azure OpenAI
    health_status["services"]["azure_openai"] = await _check_azure_openai()
    
    # Check Cosmos DB
    health_status["services"]["cosmos_db"] = await _check_cosmos_db()
    
    # Check Blob Storage
    health_status["services"]["blob_storage"] = await _check_blob_storage()
    
    # Check Content Safety
    health_status["services"]["content_safety"] = await _check_content_safety()
    
    # Determine overall status
    all_healthy = all(
        service.get("status") == "healthy" 
        for service in health_status["services"].values()
    )
    health_status["status"] = "healthy" if all_healthy else "degraded"
    
    return health_status


async def _check_key_vault() -> Dict[str, str]:
    """Check Key Vault connection"""
    if not settings.USE_KEY_VAULT:
        return {
            "status": "disabled",
            "message": "Key Vault is not enabled (USE_KEY_VAULT=false)"
        }
    
    try:
        from app.config.azure_key_vault import get_key_vault_service
        kv = get_key_vault_service()
        
        # Try to list secrets (doesn't retrieve values)
        secrets = kv.list_secrets()
        
        return {
            "status": "healthy",
            "message": f"Connected to Key Vault: {settings.AZURE_KEY_VAULT_NAME}",
            "secrets_count": len(secrets),
            "vault_uri": kv.key_vault_uri
        }
    except Exception as e:
        logger.error(f"Key Vault health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"Failed to connect to Key Vault: {str(e)}"
        }


async def _check_azure_openai() -> Dict[str, str]:
    """Check Azure OpenAI connection"""
    try:
        if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_API_KEY:
            return {
                "status": "unhealthy",
                "message": "Azure OpenAI credentials not configured"
            }
        
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )
        
        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        return {
            "status": "healthy",
            "message": "Azure OpenAI connection successful",
            "endpoint": settings.AZURE_OPENAI_ENDPOINT,
            "deployment": settings.AZURE_OPENAI_DEPLOYMENT_NAME
        }
    except Exception as e:
        logger.error(f"Azure OpenAI health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"Azure OpenAI error: {str(e)}"
        }


async def _check_cosmos_db() -> Dict[str, str]:
    """Check Cosmos DB connection"""
    try:
        if not settings.COSMOS_DB_ENDPOINT or not settings.COSMOS_DB_KEY:
            return {
                "status": "unhealthy",
                "message": "Cosmos DB credentials not configured"
            }
        
        from azure.cosmos import CosmosClient
        client = CosmosClient(
            settings.COSMOS_DB_ENDPOINT,
            settings.COSMOS_DB_KEY
        )
        
        database = client.get_database_client(settings.COSMOS_DB_DATABASE_NAME)
        database.read()
        
        return {
            "status": "healthy",
            "message": "Cosmos DB connection successful",
            "endpoint": settings.COSMOS_DB_ENDPOINT,
            "database": settings.COSMOS_DB_DATABASE_NAME
        }
    except Exception as e:
        logger.error(f"Cosmos DB health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"Cosmos DB error: {str(e)}"
        }



async def _check_blob_storage() -> Dict[str, str]:
    """Check Azure Blob Storage connection"""
    try:
        if not settings.AZURE_STORAGE_CONNECTION_STRING:
            return {
                "status": "unhealthy",
                "message": "Blob Storage connection string not configured"
            }
        
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        
        # Try to get container
        container_client = blob_service_client.get_container_client(
            settings.AZURE_STORAGE_CONTAINER_NAME
        )
        
        # Check if exists
        exists = container_client.exists()
        
        return {
            "status": "healthy",
            "message": "Blob Storage connection successful",
            "container": settings.AZURE_STORAGE_CONTAINER_NAME,
            "container_exists": exists
        }
    except Exception as e:
        logger.error(f"Blob Storage health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"Blob Storage connection failed: {str(e)}"
        }


async def _check_content_safety() -> Dict[str, str]:
    """Check Azure Content Safety connection"""
    try:
        if not settings.AZURE_CONTENT_SAFETY_ENDPOINT or not settings.AZURE_CONTENT_SAFETY_KEY:
            return {
                "status": "unhealthy",
                "message": "Content Safety credentials not configured"
            }
        
        
        url = f"{settings.AZURE_CONTENT_SAFETY_ENDPOINT}/contentsafety/text:analyze?api-version=2023-10-01"
        headers = {
            "Ocp-Apim-Subscription-Key": settings.AZURE_CONTENT_SAFETY_KEY,
            "Content-Type": "application/json"
        }
        
        data = {"text": "Hello world"}
        
        response = requests.post(url, headers=headers, json=data, timeout=5)
        
        if response.status_code == 200:
            return {
                "status": "healthy",
                "message": "Content Safety API connection successful",
                "endpoint": settings.AZURE_CONTENT_SAFETY_ENDPOINT
            }
        else:
            return {
                "status": "unhealthy",
                "message": f"Content Safety API returned status {response.status_code}"
            }
    except Exception as e:
        logger.error(f"Content Safety health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"Content Safety error: {str(e)}"
        }


@router.get("/health/keyvault", tags=["Health"])
async def keyvault_health_check() -> Dict[str, Any]:
    """
    Specific endpoint to test Key Vault connection and list secrets
    """
    if not settings.USE_KEY_VAULT:
        return {
            "enabled": False,
            "message": "Key Vault is not enabled. Set USE_KEY_VAULT=true to enable."
        }
    
    try:
        from app.config.azure_key_vault import get_key_vault_service
        kv = get_key_vault_service()
        
        # List all secrets
        secrets = kv.list_secrets()
        
        # Try to get a test secret (safely)
        test_results = []
        for secret_name in ["AZURE-OPENAI-API-KEY", "COSMOS-DB-KEY", "TELEGRAM-BOT"]:
            try:
                value = kv.get_secret_safe(secret_name)
                test_results.append({
                    "secret": secret_name,
                    "status": "found" if value else "not_found",
                    "length": len(value) if value else 0
                })
            except Exception as e:
                test_results.append({
                    "secret": secret_name,
                    "status": "error",
                    "message": str(e)
                })
        
        return {
            "enabled": True,
            "status": "healthy",
            "vault_name": os.getenv("AZURE_KEY_VAULT_NAME"),
            "vault_uri": kv.key_vault_uri,
            "total_secrets": len(secrets),
            "secret_names": secrets,
            "test_results": test_results
        }
    except Exception as e:
        logger.error(f"Key Vault health check failed: {str(e)}")
        return {
            "enabled": True,
            "status": "unhealthy",
            "error": str(e),
            "vault_name": os.getenv("AZURE_KEY_VAULT_NAME")
        }

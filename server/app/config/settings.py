# Environment variables & Azure config
# app/config/settings.py

import os
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings with support for Azure Key Vault.
    Reads from .env file in development or Azure Key Vault in production.
    """
    
    # ========================================================================
    # General Settings
    # ========================================================================
    SERVICE_NAME: str = "civi-chat-api"
    ENVIRONMENT: str = "development"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # ========================================================================
    # Database
    # ========================================================================
    DATABASE_URL: str = "sqlite:///./civi-chat.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # ========================================================================
    # Azure Key Vault
    # ========================================================================
    USE_KEY_VAULT: bool = False
    AZURE_KEY_VAULT_NAME: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None
    
    # ========================================================================
    # Azure Content Safety
    # ========================================================================
    AZURE_CONTENT_SAFETY_ENDPOINT: Optional[str] = None
    AZURE_CONTENT_SAFETY_KEY: Optional[str] = None
    
    # ========================================================================
    # Azure Blob Storage
    # ========================================================================
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER_NAME: str = "documents"
    
    # ========================================================================
    # Azure Cosmos DB
    # ========================================================================
    COSMOS_DB_ENDPOINT: Optional[str] = None
    COSMOS_DB_KEY: Optional[str] = None
    COSMOS_DB_DATABASE_NAME: str = "civic_chat"
    COSMOS_DB_DOCUMENTS_CONTAINER: str = "documents"
    COSMOS_DB_CONVERSATIONS_CONTAINER: str = "conversations"
    COSMOS_DB_NOTIFICATIONS_CONTAINER: str = "notifications"
    COSMOS_DB_MESSAGES_CONTAINER: str = "messages"
    COSMOS_DB_USERS_CONTAINER: str = "users"
    
    # ========================================================================
    # Azure OpenAI
    # ========================================================================
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-ada-002"
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"
    
    # ========================================================================
    # Azure AI Search
    # ========================================================================
    AZURE_SEARCH_ENDPOINT: Optional[str] = None
    AZURE_SEARCH_KEY: Optional[str] = None
    AZURE_SEARCH_INDEX_NAME: str = "government-data"
    
    # ========================================================================
    # Telegram
    # ========================================================================
    TELEGRAM_BOT: Optional[str] = None
    # Azure Search
    AZURE_SEARCH_ENDPOINT: str = ""
    AZURE_SEARCH_API_KEY: str = ""
    AZURE_SEARCH_INDEX_NAME: str = ""
    
    # Azure Cosmos DB SQL API
    COSMOS_ENDPOINT: str = ""
    COSMOS_KEY: str = ""
    COSMOS_DATABASE_NAME: str = "civicflowcosmodb"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# ============================================================================
# Singleton instance with Key Vault support
# ============================================================================
_settings_instance: Optional[Settings] = None


@lru_cache()
def get_settings() -> Settings:
    """
    Get or create settings instance with Key Vault support.
    Reads secrets from Key Vault if USE_KEY_VAULT=true, otherwise from .env
    """
    global _settings_instance
    
    if _settings_instance is None:
        # Load base settings from .env
        _settings_instance = Settings()
        
        # Override with Key Vault secrets if enabled
        if _settings_instance.USE_KEY_VAULT:
            _load_secrets_from_keyvault(_settings_instance)
    
    return _settings_instance


def _load_secrets_from_keyvault(settings_obj: Settings):
    """Load secrets from Azure Key Vault and override settings"""
    try:
        from app.config.azure_key_vault import get_key_vault_service
        kv = get_key_vault_service()
        
        # Map of settings attributes to Key Vault secret names
        secret_mappings = {
            "AZURE_CONTENT_SAFETY_KEY": "AZURE-CONTENT-SAFETY-KEY",
            "AZURE_STORAGE_CONNECTION_STRING": "AZURE-STORAGE-CONNECTION-STRING",
            "COSMOS_DB_KEY": "COSMOS-DB-KEY",
            "AZURE_OPENAI_API_KEY": "AZURE-OPENAI-API-KEY",
            "AZURE_SEARCH_KEY": "AZURE-SEARCH-KEY",
            "TELEGRAM_BOT": "TELEGRAM-BOT",
        }
        
        # Load each secret and override
        for attr_name, secret_name in secret_mappings.items():
            try:
                secret_value = kv.get_secret(secret_name)
                setattr(settings_obj, attr_name, secret_value)
                print(f"✅ Loaded {attr_name} from Key Vault")
            except Exception as e:
                print(f"⚠️  Could not load {secret_name} from Key Vault: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error loading secrets from Key Vault: {str(e)}")
        print("⚠️  Falling back to environment variables")


# Export singleton instance
settings = get_settings()



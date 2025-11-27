# Environment variables & Azure config
# app/config/settings.py

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Service settings
    SERVICE_NAME: str = "civi-chat-api"
    ENVIRONMENT: str = "development"
    
    # Azure OpenTelemetry
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    ALLOWED_ORIGINS: list[str] = ["*"]
    
    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"
    
    # OpenAI (alternativa a Azure)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"  # o gpt-4, gpt-3.5-turbo, etc.
    
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

settings = Settings()

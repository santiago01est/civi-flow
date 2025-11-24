# Environment variables & Azure config
# app/config/settings.py

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Service settings
    SERVICE_NAME: str = "civi-chat-api"
    ENVIRONMENT: str = "development"
    
    # Azure Cosmos DB
    COSMOS_DB_ENDPOINT: str = ""
    COSMOS_DB_KEY: str = ""
    COSMOS_DB_DATABASE_NAME: str = "civi-flow"
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173"]
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

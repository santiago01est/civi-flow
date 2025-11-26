import os
import logging
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from typing import Optional

logger = logging.getLogger(__name__)


class AzureKeyVaultService:
    """
    Service to retrieve secrets from Azure Key Vault.
    Supports both Managed Identity (production) and Service Principal (local dev).
    """
    
    def __init__(self):
        self.key_vault_name = os.getenv("AZURE_KEY_VAULT_NAME")
        
        if not self.key_vault_name:
            raise ValueError(
                "AZURE_KEY_VAULT_NAME environment variable is required when USE_KEY_VAULT=true"
            )
        
        self.key_vault_uri = f"https://{self.key_vault_name}.vault.azure.net"
        self.client = self._create_secret_client()
        logger.info(f"Azure Key Vault client initialized for: {self.key_vault_uri}")
    
    def _create_secret_client(self) -> SecretClient:
        """
        Create SecretClient with appropriate credentials.
        Uses Service Principal in local dev, Managed Identity in Azure.
        """
        credential = self._get_credential()
        return SecretClient(vault_url=self.key_vault_uri, credential=credential)
    
    def _get_credential(self):
        """
        Get authentication credential based on environment.
        Priority:
        1. Service Principal (if AZURE_CLIENT_ID is set) - for local dev
        2. DefaultAzureCredential (Managed Identity, Azure CLI, etc.) - for production
        """
        client_id = os.getenv("AZURE_CLIENT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        tenant_id = os.getenv("AZURE_TENANT_ID")
        
        # If all Service Principal credentials are provided, use them (local dev)
        if client_id and client_secret and tenant_id:
            logger.info("Using Service Principal authentication for Key Vault")
            return ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
        else:
            # Use DefaultAzureCredential (works with Managed Identity in Azure)
            logger.info("Using DefaultAzureCredential for Key Vault (Managed Identity or Azure CLI)")
            return DefaultAzureCredential()
    
    def get_secret(self, secret_name: str) -> str:
        """
        Retrieve a secret from Azure Key Vault.
        
        Args:
            secret_name: Name of the secret in Key Vault (e.g., "AZURE-OPENAI-API-KEY")
        
        Returns:
            Secret value as string
        
        Raises:
            Exception if secret cannot be retrieved
        """
        try:
            secret = self.client.get_secret(secret_name)
            logger.debug(f"Successfully retrieved secret: {secret_name}")
            return secret.value
        except Exception as e:
            logger.error(f"Error retrieving secret '{secret_name}' from Key Vault: {str(e)}")
            raise Exception(f"Failed to retrieve secret '{secret_name}': {str(e)}")
    
    def get_secret_safe(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a secret safely, returning default value if it fails.
        Useful for non-critical secrets.
        
        Args:
            secret_name: Name of the secret in Key Vault
            default: Default value to return if secret cannot be retrieved
        
        Returns:
            Secret value or default value
        """
        try:
            return self.get_secret(secret_name)
        except Exception as e:
            logger.warning(f"Could not retrieve secret '{secret_name}', using default value")
            return default
    
    def list_secrets(self) -> list:
        """
        List all secret names in the Key Vault (useful for debugging).
        Does not return secret values, only names.
        
        Returns:
            List of secret names
        """
        try:
            secret_properties = self.client.list_properties_of_secrets()
            secret_names = [secret.name for secret in secret_properties]
            logger.info(f"Found {len(secret_names)} secrets in Key Vault")
            return secret_names
        except Exception as e:
            logger.error(f"Error listing secrets: {str(e)}")
            return []


# ============================================================================
# Singleton Pattern - Only create one instance
# ============================================================================
_key_vault_service_instance: Optional[AzureKeyVaultService] = None


def get_key_vault_service() -> AzureKeyVaultService:
    """
    Get or create singleton instance of AzureKeyVaultService.
    
    Returns:
        AzureKeyVaultService instance
    """
    global _key_vault_service_instance
    
    if _key_vault_service_instance is None:
        _key_vault_service_instance = AzureKeyVaultService()
    
    return _key_vault_service_instance


def reset_key_vault_service():
    """
    Reset singleton instance (useful for testing).
    """
    global _key_vault_service_instance
    _key_vault_service_instance = None

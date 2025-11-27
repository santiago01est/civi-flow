# Azure Content Safety
import os
import aiohttp
from app.config.settings import settings
AZURE_CONTENT_SAFETY_ENDPOINT = settings.AZURE_CONTENT_SAFETY_ENDPOINT
AZURE_CONTENT_SAFETY_KEY = settings.AZURE_CONTENT_SAFETY_KEY

class ContentSafetyService:
    """Service to validate text safety with Azure Content Safety API"""

    async def validate_text(self, text: str) -> bool:
        """
        Returns True if text is safe, False if it contains restricted content.
        """
        url = f"{AZURE_CONTENT_SAFETY_ENDPOINT}/contentsafety/text:analyze?api-version=2023-10-01"
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_CONTENT_SAFETY_KEY,
            "Content-Type": "application/json"
        }
        data = {"text": text[:8192]}  # Azure Content Safety has a payload limit, truncate if needed

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    # Check any category detected with severity >= 2 (you can adjust threshold)
                    for cat in result.get("categoriesAnalysis", []):
                        if cat["severity"] >= 2:
                            return False
                    return True
                else:
                    return False  # default to unsafe if call fails

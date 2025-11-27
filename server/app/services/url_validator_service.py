import aiohttp
import re

# example: only allow .gov, .gob, .gov.co domains
ALLOWED_DOMAINS = [
    r"\.gov", r"\.gob", r"\.gov\.co"
]

class URLValidatorService:
    """Service to validate if a URL is safe and governmental"""

    async def validate_url(self, url: str) -> bool:
        """
        Returns True if the URL is in the government whitelist and is reachable.
        """
        # Check if in allowed domains
        if not any(re.search(domain, url) for domain in ALLOWED_DOMAINS):
            return False

        # Basic reachability check
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        return True
        except Exception:
            pass

        return False

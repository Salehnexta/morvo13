from typing import Any

import httpx

from app.core.config.settings import settings
from app.core.exceptions import ServiceError


class PerplexityService:
    def __init__(self) -> None:
        self.api_key = settings.PERPLEXITY_API_KEY
        if not self.api_key:
            raise ServiceError("PERPLEXITY_API_KEY is not set in the environment.")

        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=60.0)

    async def analyze_website(self, website_url: str) -> dict[str, Any]:
        prompt = f"""
        Analyze the business website: {website_url}
        
        Extract the following information:
        1. Business description and services
        2. Industry classification
        3. Target market and audience
        4. Contact information
        5. Social media presence
        6. Main competitors mentioned
        7. Key differentiators
        8. Geographic focus/location
        
        Focus on factual information that would be useful for marketing strategy.
        Consider Saudi Arabian business context if applicable.
        """

        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": "llama-3.1-sonar-large-128k-online",
                    "messages": [{"role": "user", "content": prompt}],
                    "return_citations": True,
                    "search_domain_filter": ["company website", "business directory"],
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"API Error: {e.response.status_code} - {e.response.text}",
            }
        except httpx.RequestError as e:
            raise ServiceError(f"Failed to connect to Perplexity API: {e}") from e

    async def close(self) -> None:
        await self.client.aclose()

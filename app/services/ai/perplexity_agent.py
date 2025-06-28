import json
import logging
from typing import Any

import httpx

from app.core.config.settings import settings

logger = logging.getLogger(__name__)


class PerplexityIntelligenceAgent:
    def __init__(self) -> None:
        self.api_key = settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai"
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)

    async def analyze_website(self, website_url: str) -> dict[str, Any]:
        prompt = f"""
        Analyze the business website: {website_url}
        
        Extract the following information in a structured JSON format:
        {{
            "business_description": "",
            "industry_classification": "",
            "target_market_insights": "",
            "competitor_names": [],
            "contact_info": {{
                "email": "",
                "phone": ""
            }},
            "market_positioning": "",
            "geographic_focus": "",
            "services_offered": []
        }}
        
        Focus on factual information that would be useful for marketing strategy.
        Consider Saudi Arabian business context if applicable.
        """

        try:
            response = await self.client.post(
                "/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-sonar-large-128k-online",
                    "messages": [{"role": "user", "content": prompt}],
                    "return_citations": True,
                    "search_domain_filter": ["company website", "business directory"],
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()

            raw_response = response.json()
            content = raw_response["choices"][0]["message"]["content"]

            # Attempt to parse JSON from the content
            try:
                # Perplexity might return text before/after JSON, so find the JSON part
                json_match = content.find("{")
                json_content = content[json_match:]
                parsed_data = json.loads(json_content)
                return {"success": True, "data": parsed_data, "raw_response": raw_response}
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from Perplexity response: {content}")
                return {
                    "success": False,
                    "error": "Failed to parse structured data from Perplexity",
                    "raw_response": raw_response,
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"Perplexity API HTTP error: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"Perplexity API error: {e.response.status_code} - {e.response.text}",
            }
        except httpx.RequestError as e:
            logger.error(f"Perplexity API request error: {e}")
            return {"success": False, "error": f"Perplexity API request failed: {e}"}
        except Exception as e:
            logger.error(f"Unexpected error during Perplexity analysis: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    async def close(self) -> None:
        await self.client.aclose()

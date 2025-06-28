from typing import Any

from app.services.perplexity_service import PerplexityService
from app.services.seranking_service import SERankingService


class MasterAgent:
    def __init__(self) -> None:
        self.seranking_service = SERankingService()
        self.perplexity_service = PerplexityService()

    async def process_request(self, user_input: str, website_url: str) -> dict[str, Any]:
        """
        Processes a user request, orchestrating calls to backend services
        and synthesizing information to provide a comprehensive response.
        """
        perplexity_data = await self.perplexity_service.analyze_website(website_url)

        # SE Ranking analysis
        se_ranking_data = await self.seranking_service.analyze_backlinks(website_url)

        # Synthesize data (simplified for now)
        response_data = {
            "message": f"Analyzing {website_url} for you.",
            "se_ranking_summary": se_ranking_data.get("data"),
            "perplexity_summary": perplexity_data.get("data"),
            "recommendations": "Further analysis needed to provide specific recommendations.",
        }

        return response_data

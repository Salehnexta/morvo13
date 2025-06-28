import asyncio
import json
import logging
from typing import Any

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic.v1.types import SecretStr

from app.core.config.settings import settings
from app.services.ai.cultural_context_agent import CulturalContextAgent
from app.services.ai.perplexity_agent import PerplexityIntelligenceAgent
from app.services.ai.seranking_processor_agent import SERankingProcessorAgent

logger = logging.getLogger(__name__)


class DataSynthesisAgent:
    def __init__(self) -> None:
        self.perplexity_agent = PerplexityIntelligenceAgent()
        self.seranking_agent = SERankingProcessorAgent()
        self.cultural_agent = CulturalContextAgent()
        self.llm = ChatOpenAI(api_key=SecretStr(settings.OPENAI_API_KEY), model=settings.GPT_4O_MODEL)

    async def synthesize_website_analysis(self, domain: str, user_id: str) -> dict[str, Any]:
        # Run Perplexity and SE Ranking analyses concurrently
        perplexity_task = self.perplexity_agent.analyze_website(domain)
        seranking_task = self.seranking_agent.analyze_backlinks(domain)

        perplexity_result, seranking_result = await asyncio.gather(perplexity_task, seranking_task)

        synthesized_data: dict[str, Any] = {
            "domain": domain,
            "user_id": user_id,
            "perplexity_analysis": perplexity_result,
            "seranking_analysis": seranking_result,
            "cultural_insights": {},
            "opportunities": [],
            "pain_points": [],
        }

        # Add cultural insights to the synthesized data
        if perplexity_result.get("success") and "data" in perplexity_result:
            business_desc = perplexity_result["data"].get("business_description", "")
            synthesized_data["cultural_insights"]["business_description_cultural_analysis"] = (
                self.cultural_agent.analyze_text_for_cultural_relevance(business_desc)
            )

        if seranking_result.get("success") and "data" in seranking_result:
            synthesized_data["cultural_insights"]["seranking_cultural_analysis"] = seranking_result[
                "data"
            ].get("saudi_market_analysis", {})

        # Use GPT-4o to synthesize insights
        opportunities, pain_points = await self._synthesize_with_gpt4o(synthesized_data)
        synthesized_data["opportunities"] = opportunities
        synthesized_data["pain_points"] = pain_points

        return {"success": True, "data": synthesized_data}

    async def _synthesize_with_gpt4o(self, data: dict[str, Any]) -> tuple[list[str], list[str]]:
        prompt = f"""
        You are a PhD-level marketing consultant specializing in the Saudi Arabian market.
        Your goal is to analyze the provided data and identify key marketing opportunities and pain points.
        Present your findings in a friendly tone, suitable for a Saudi business owner.
        
        Here is the data:
        Perplexity Analysis: {json.dumps(data.get("perplexity_analysis"))}
        SE Ranking Analysis: {json.dumps(data.get("seranking_analysis"))}
        Cultural Insights: {json.dumps(data.get("cultural_insights"))}
        
        Based on this, provide a list of:
        1. Marketing Opportunities (e.g., "Expand into Arabic content marketing for untapped local keywords.")
        2. Marketing Pain Points (e.g., "Low domain authority due to lack of quality backlinks.")
        
        Format your response as a JSON object with two keys: "opportunities" and "pain_points".
        Example: {{\"opportunities\": [\"Opportunity 1\"], \"pain_points\": [\"Pain Point 1\"]}}
        """

        try:
            response = await self.llm.agenerate(messages=[[HumanMessage(content=prompt)]])

            # Assuming the response content is a JSON string
            content = response.generations[0][0].text
            parsed_response = json.loads(content)

            opportunities = parsed_response.get("opportunities", [])
            pain_points = parsed_response.get("pain_points", [])

            return opportunities, pain_points

        except Exception as e:
            logger.error(f"Error synthesizing with GPT-4o: {e}")
            return ["Error synthesizing opportunities"], ["Error synthesizing pain points"]

    async def close(self) -> None:
        await self.perplexity_agent.close()
        await self.seranking_agent.close()

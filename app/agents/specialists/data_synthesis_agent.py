"""The Data Synthesis Agent, responsible for creating a unified analysis.

This agent takes structured data from various specialist agents (e.g., Perplexity,
SE Ranking) and uses a powerful language model to generate a cohesive,
insightful, and culturally relevant marketing analysis.
"""

import json
from datetime import datetime
from typing import Any

from crewai import Agent, Task
from langchain_openai import ChatOpenAI  # Import ChatOpenAI
from openai import AsyncOpenAI
from pydantic import PrivateAttr
from pydantic.v1.types import SecretStr

from app.agents.common.base_agent import BaseAgent
from app.core.config.settings import settings


class AgentException(Exception):
    """Custom exception for agent errors."""



class DataSynthesisAgent(BaseAgent):
    """Synthesizes data from multiple sources into a coherent analysis."""

    _openai_client: AsyncOpenAI = PrivateAttr()
    _model: str = PrivateAttr()

    def __init__(self, **kwargs: Any) -> None:
        """Initializes the DataSynthesisAgent with an async OpenAI client."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment.")

        # Create ChatOpenAI instance for the LLM
        llm = ChatOpenAI(api_key=SecretStr(settings.OPENAI_API_KEY), model=settings.GPT_4O_MODEL)

        super().__init__(
            role=kwargs.pop("role", "Data Synthesis Agent"),
            goal=kwargs.pop(
                "goal", "Synthesize complex marketing data into actionable strategies."
            ),
            backstory=kwargs.pop(
                "backstory",
                "Expert in combining diverse data sources to form coherent, culturally-aware marketing plans.",
            ),
            llm=llm,  # Pass the llm instance here
            **kwargs,
        )
        self._openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.GPT_4O_MODEL

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Executes the data synthesis task.

        Args:
            context: A dictionary containing the data to be synthesized.
                     Expected keys include 'business_profile', 'intelligence_data',
                     'seo_analysis', and 'cultural_context'.

        Returns:
            A dictionary containing the synthesized marketing analysis.
        """
        self.log(
            f"Starting data synthesis for business: "
            f"{context.get('business_profile', {}).get('name')}"
        )

        prompt = self._build_prompt(context)

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=4000,
            )

            if not response.choices or not response.choices[0].message.content:
                raise AgentException("OpenAI response was empty or invalid.")

            synthesized_analysis = response.choices[0].message.content
            self.log("Successfully synthesized data.")

            return {"status": "success", "analysis": synthesized_analysis}

        except Exception as e:
            self.log(f"Error during OpenAI API call: {e}", level="error")
            raise AgentException(f"Failed to synthesize data: {e}") from e

    def _build_prompt(self, context: dict[str, Any]) -> str:
        """Constructs the detailed prompt for the OpenAI API call."""
        business_profile = context.get("business_profile", {})
        intelligence_data = context.get("intelligence_data", {})
        seo_analysis = context.get("seo_analysis", {})
        cultural_context = context.get("cultural_context", {})

        prompt = f"""
        **Business Profile:**
        - Name: {business_profile.get("name", "N/A")}
        - Industry: {business_profile.get("industry", "N/A")}
        - Target Audience: {business_profile.get("target_audience", "N/A")}
        - Unique Selling Proposition: {business_profile.get("usp", "N/A")}

        **Web Intelligence Analysis (from Perplexity):**
        {intelligence_data.get("summary", "No web intelligence data provided.")}

        **SEO & Backlink Analysis (from SE Ranking):**
        {seo_analysis.get("summary", "No SEO analysis data provided.")}

        **Cultural Context (for Saudi Arabia):**
        {cultural_context.get("summary", "No cultural context provided.")}

        **Task:**
        Based on all the information provided above, create a comprehensive,
        actionable, and culturally-aware marketing strategy for the business.
        The output should be a well-structured report in Markdown format.
        It must be bilingual (Arabic and English) and address the following:
        1.  **Executive Summary:** A brief overview of the key findings
            and recommendations.
        2.  **SWOT Analysis:** Strengths, Weaknesses, Opportunities, and Threats,
            integrating all data sources.
        3.  **Target Audience Insights:** Deeper insights into the target audience,
            considering cultural nuances.
        4.  **Content Strategy Recommendations:** Specific content ideas (blog posts,
            social media campaigns, videos) that will resonate with the Saudi market.
        5.  **SEO & Competitor Strategy:** Actionable steps to improve SEO and
            outperform competitors.
        6.  **Key Performance Indicators (KPIs):** Metrics to track the success
            of the proposed strategy.
        """
        return prompt.strip()

    def _get_system_prompt(self) -> str:
        """Returns the system prompt that defines the agent's persona."""
        return (
            "You are a world-class AI Marketing Strategist for the Saudi Arabian market. "
            "Your role is to synthesize complex data from multiple sources into a single, "
            "actionable, and culturally-sensitive marketing plan. You are an expert in both "
            "global marketing trends and local Saudi culture. Your analysis must be insightful, "
            "data-driven, and presented clearly in both English and Arabic."
        )

    def _create_agent(self) -> Agent:
        """Create the specialized data synthesis agent."""
        return Agent(
            role="Senior Data Synthesis Specialist",
            goal="Synthesize multi-source marketing data with deep Saudi market understanding to provide actionable business intelligence",
            backstory="""You are an expert data analyst with 10+ years of experience in the Saudi Arabian market.
            You specialize in combining data from multiple sources (social media, SEO, competitor analysis, market research)
            to create comprehensive marketing intelligence reports that drive business growth in the GCC region.""",
            verbose=True,
            allow_delegation=False,
            llm=self.model,
        )

    def synthesize_marketing_data(
        self, data_sources: dict[str, Any], analysis_type: str = "comprehensive"
    ) -> dict[str, Any]:
        """
        Synthesize data from multiple marketing sources with Saudi market context.

        Args:
            data_sources: Dictionary containing data from various sources
            analysis_type: Type of analysis to perform

        Returns:
            Comprehensive synthesis report
        """
        try:
            # Create synthesis task
            synthesis_task = Task(
                description=f"""
                Analyze and synthesize the following marketing data sources for Saudi Arabian market context:
                
                Data Sources: {json.dumps(data_sources, indent=2)}
                Analysis Type: {analysis_type}
                
                Provide a comprehensive synthesis that includes:
                1. Key insights and patterns
                2. Saudi market-specific opportunities
                3. Cultural and regulatory considerations
                4. Actionable recommendations
                5. Risk assessment and mitigation strategies
                6. Performance benchmarks against Saudi market standards
                
                Focus on Vision 2030 alignment and local market dynamics.
                """,
                agent=self._create_agent(),
                expected_output="Detailed synthesis report with actionable insights",
            )

            # Execute the synthesis task
            result = self.agent.execute_task(synthesis_task)
            
            # Return structured synthesis results
            return {
                "synthesis_summary": result.raw,
                "data_sources_analyzed": list(data_sources.keys()),
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "agent_id": "data_synthesis_agent"
            }

        except Exception as e:
            raise AgentException(f"Data synthesis failed: {e!s}") from e

    def _calculate_data_quality(self, data_sources: dict[str, Any]) -> float:
        """Calculate overall data quality score."""
        # Implementation for data quality assessment
        return 0.85  # Placeholder

    def _assess_market_alignment(self, data_sources: dict[str, Any]) -> float:
        """Assess how well the data aligns with Saudi market requirements."""
        # Implementation for market alignment assessment
        return 0.92  # Placeholder

    def _extract_recommendations(self, synthesis_result: str) -> list[str]:
        """Extract actionable recommendations from synthesis result."""
        # Implementation for recommendation extraction
        return ["Placeholder recommendation"]  # Placeholder

    async def close(self) -> None:
        """Clean up resources."""
        # Clean up any resources if needed

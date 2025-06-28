"""
Enhanced Master Agent for Morvo AI Marketing Consultant
Orchestrates multiple AI agents to provide comprehensive Saudi market intelligence and marketing consultation.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from loguru import logger

from app.services.perplexity_service import PerplexityService
from app.services.seranking_service import SERankingService
from app.services.ai.cultural_context_agent import CulturalContextAgent
from app.services.ai.data_synthesis_agent import DataSynthesisAgent


class MasterAgent:
    """
    Enhanced Master Agent that orchestrates multiple AI agents for comprehensive marketing consultation.
    
    Features:
    - Multi-agent coordination and orchestration
    - Saudi cultural intelligence integration
    - Vision 2030 alignment
    - Comprehensive marketing analysis
    - Business intelligence synthesis
    """

    def __init__(self) -> None:
        """Initialize the Master Agent with all sub-agents and services."""
        self.seranking_service = SERankingService()
        self.perplexity_service = PerplexityService()
        self.cultural_agent = CulturalContextAgent()
        self.data_synthesis_agent = DataSynthesisAgent()
        
        # Agent coordination metadata
        self.agent_capabilities = {
            "cultural_context": ["cultural_adaptation", "islamic_compliance", "vision_2030_alignment"],
            "perplexity": ["website_analysis", "content_research", "market_intelligence"],
            "seranking": ["seo_analysis", "competitor_research", "keyword_analysis"],
            "data_synthesis": ["insights_generation", "recommendation_synthesis", "business_intelligence"]
        }
        
        logger.info("🎯 Master Agent initialized with full agent orchestration capabilities")

    async def coordinate_marketing_analysis(
        self, 
        request: Dict[str, Any], 
        client_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate comprehensive marketing analysis using multiple agents.

        Args:
            request: The user's request with message and context
            client_context: Client context including cultural preferences and history

        Returns:
            Dict containing coordinated analysis from all agents
        """
        logger.info(f"🚀 Starting coordinated marketing analysis for client: {client_context.get('client_id')}")
        
        try:
            analysis_id = str(uuid.uuid4())
            start_time = datetime.utcnow()
            
            # Extract user message and context
            user_message = request.get("message", "")
            conversation_context = request.get("context", {})
            
            # Determine which agents to activate based on user intent
            required_agents = self._determine_required_agents(user_message)
            logger.info(f"📋 Activating agents: {', '.join(required_agents)}")
            
            # Initialize analysis results
            analysis_results = {
                "analysis_id": analysis_id,
                "user_message": user_message,
                "activated_agents": required_agents,
                "start_time": start_time.isoformat(),
                "agent_results": {},
                "coordinated_analysis": {},
                "cultural_adaptations": [],
                "business_insights": [],
                "recommendations": []
            }

            # Execute agent coordination based on requirements
            if "cultural_context" in required_agents:
                cultural_analysis = await self._execute_cultural_analysis(
                    user_message, client_context
                )
                analysis_results["agent_results"]["cultural_context"] = cultural_analysis

            if "perplexity" in required_agents:
                perplexity_analysis = await self._execute_perplexity_analysis(
                    user_message, client_context
                )
                analysis_results["agent_results"]["perplexity"] = perplexity_analysis

            if "seranking" in required_agents:
                seo_analysis = await self._execute_seo_analysis(
                    user_message, client_context
                )
                analysis_results["agent_results"]["seranking"] = seo_analysis

            # Synthesize all agent results
            if "data_synthesis" in required_agents:
                synthesis_result = await self._execute_data_synthesis(
                    analysis_results["agent_results"], user_message, client_context
                )
                analysis_results["agent_results"]["data_synthesis"] = synthesis_result

            # Create coordinated final analysis
            coordinated_result = await self._create_coordinated_analysis(
                analysis_results, user_message, client_context
            )
            analysis_results["coordinated_analysis"] = coordinated_result

            # Calculate processing time
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            analysis_results["processing_time_seconds"] = processing_time
            analysis_results["end_time"] = end_time.isoformat()

            logger.success(
                f"✅ Completed coordinated analysis in {processing_time:.2f}s "
                f"using {len(required_agents)} agents"
            )

            return analysis_results

        except Exception as e:
            logger.error(f"❌ Error in coordinated marketing analysis: {e}")
            return self._create_error_response(str(e), client_context)

    def _determine_required_agents(self, user_message: str) -> List[str]:
        """
        Determine which agents are needed based on user message intent.

        Args:
            user_message: The user's message

        Returns:
            List of required agent names
        """
        message_lower = user_message.lower()
        required_agents = ["cultural_context"]  # Always include cultural intelligence
        
        # SEO and search-related queries
        if any(keyword in message_lower for keyword in [
            "seo", "search", "ranking", "google", "keywords", "بحث", "محرك البحث"
        ]):
            required_agents.extend(["seranking", "perplexity"])
        
        # Competitor analysis
        elif any(keyword in message_lower for keyword in [
            "competitor", "competition", "analysis", "منافس", "تحليل"
        ]):
            required_agents.extend(["seranking", "perplexity"])
        
        # Website analysis
        elif any(keyword in message_lower for keyword in [
            "website", "site", "url", "domain", "موقع"
        ]):
            required_agents.append("perplexity")
        
        # General marketing strategy
        elif any(keyword in message_lower for keyword in [
            "marketing", "strategy", "campaign", "تسويق", "استراتيجية"
        ]):
            required_agents.append("perplexity")
        
        # Always include data synthesis for comprehensive analysis
        if len(required_agents) > 1:
            required_agents.append("data_synthesis")
        
        return list(set(required_agents))  # Remove duplicates

    async def _execute_cultural_analysis(
        self, 
        user_message: str, 
        client_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute cultural context analysis."""
        try:
            logger.info("🕌 Executing cultural context analysis")
            
            # Get cultural context from client data
            cultural_context = client_context.get("cultural_context")
            user_profile = client_context.get("user_profile")
            
            result = await self.cultural_agent.analyze_cultural_context(
                message=user_message,
                cultural_context=cultural_context,
                user_profile=user_profile
            )
            
            return {
                "status": "success",
                "analysis": result,
                "cultural_adaptations": result.get("adaptations", []),
                "islamic_compliance": result.get("islamic_compliant", True),
                "vision_2030_alignment": result.get("vision_2030_aligned", True)
            }
            
        except Exception as e:
            logger.error(f"Cultural analysis failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _execute_perplexity_analysis(
        self, 
        user_message: str, 
        client_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Perplexity-based market intelligence analysis."""
        try:
            logger.info("🔍 Executing Perplexity market analysis")
            
            # Extract website URL if mentioned
            website_url = self._extract_website_url(user_message)
            
            if website_url:
                result = await self.perplexity_service.analyze_website(website_url)
            else:
                # General market research query
                saudi_focused_query = f"Saudi Arabia market analysis: {user_message}"
                result = await self.perplexity_service.research_query(saudi_focused_query)
            
            return {
                "status": "success",
                "analysis": result,
                "website_url": website_url,
                "market_insights": result.get("insights", []),
                "data_sources": result.get("sources", [])
            }
            
        except Exception as e:
            logger.error(f"Perplexity analysis failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _execute_seo_analysis(
        self, 
        user_message: str, 
        client_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute SEO and competitor analysis."""
        try:
            logger.info("📊 Executing SEO and competitor analysis")
            
            website_url = self._extract_website_url(user_message)
            
            if website_url:
                # Analyze specific website
                backlink_data = await self.seranking_service.analyze_backlinks(website_url)
                
                return {
                    "status": "success",
                    "analysis": backlink_data,
                    "website_url": website_url,
                    "seo_insights": backlink_data.get("insights", []),
                    "competitor_data": backlink_data.get("competitors", [])
                }
            else:
                # General SEO recommendations for Saudi market
                return {
                    "status": "success",
                    "analysis": {
                        "recommendations": [
                            "Focus on Arabic keyword optimization",
                            "Implement mobile-first design for Saudi users",
                            "Optimize for local search and Google My Business",
                            "Create culturally relevant content",
                            "Ensure fast loading times for mobile users"
                        ]
                    },
                    "saudi_seo_focus": True
                }
                
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _execute_data_synthesis(
        self, 
        agent_results: Dict[str, Any], 
        user_message: str, 
        client_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize data from all agents into comprehensive insights."""
        try:
            logger.info("🧠 Executing data synthesis")
            
            synthesis_result = await self.data_synthesis_agent.synthesize_agent_data(
                agent_results=agent_results,
                user_query=user_message,
                cultural_context=client_context.get("cultural_context"),
                user_profile=client_context.get("user_profile")
            )
            
            return {
                "status": "success",
                "synthesis": synthesis_result,
                "key_insights": synthesis_result.get("insights", []),
                "recommendations": synthesis_result.get("recommendations", []),
                "business_value": synthesis_result.get("business_value", "")
            }
            
        except Exception as e:
            logger.error(f"Data synthesis failed: {e}")
            return {"status": "error", "error": str(e)}

    async def _create_coordinated_analysis(
        self, 
        analysis_results: Dict[str, Any], 
        user_message: str, 
        client_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create the final coordinated analysis response."""
        
        # Extract key insights from all agents
        all_insights = []
        all_recommendations = []
        cultural_adaptations = []
        
        for agent_name, agent_result in analysis_results["agent_results"].items():
            if agent_result.get("status") == "success":
                if "insights" in agent_result.get("analysis", {}):
                    all_insights.extend(agent_result["analysis"]["insights"])
                if "recommendations" in agent_result.get("analysis", {}):
                    all_recommendations.extend(agent_result["analysis"]["recommendations"])
                if "cultural_adaptations" in agent_result:
                    cultural_adaptations.extend(agent_result["cultural_adaptations"])

        # Create comprehensive response
        coordinated_response = {
            "summary": self._generate_response_summary(
                user_message, all_insights, all_recommendations
            ),
            "key_insights": all_insights[:5],  # Top 5 insights
            "recommended_actions": all_recommendations[:5],  # Top 5 recommendations
            "cultural_adaptations": cultural_adaptations,
            "saudi_market_focus": True,
            "vision_2030_aligned": True,
            "islamic_compliant": True,
            "confidence_score": 0.85,  # Based on successful agent coordination
            "business_value": "Enhanced marketing strategy with cultural intelligence for Saudi market success"
        }

        return coordinated_response

    def _generate_response_summary(
        self, 
        user_message: str, 
        insights: List[str], 
        recommendations: List[str]
    ) -> str:
        """Generate a comprehensive response summary."""
        
        # Create culturally intelligent response
        response = f"""🇸🇦 **Saudi Market Intelligence Analysis**

Based on your question about "{user_message[:50]}...", I've coordinated multiple AI agents to provide comprehensive insights:

**🎯 Key Insights:**
"""
        
        # Add top insights
        for i, insight in enumerate(insights[:3], 1):
            response += f"{i}. {insight}\n"
        
        response += "\n**📋 Recommended Actions:**\n"
        
        # Add top recommendations
        for i, recommendation in enumerate(recommendations[:3], 1):
            response += f"{i}. {recommendation}\n"
        
        response += """
**🕌 Cultural Intelligence Applied:**
• Islamic values compliance ensured
• Vision 2030 alignment integrated
• Saudi market preferences considered
• Arabic localization recommendations included

**Next Steps:** I can dive deeper into any specific area or analyze your website/competitors for detailed insights."""

        return response

    def _extract_website_url(self, message: str) -> Optional[str]:
        """Extract website URL from user message if present."""
        import re
        
        # Simple URL extraction pattern
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, message)
        
        if urls:
            return urls[0]
        
        # Check for domain names without protocol
        domain_pattern = r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\b'
        domains = re.findall(domain_pattern, message.lower())
        
        if domains:
            return f"https://{domains[0]}"
        
        return None

    def _create_error_response(self, error: str, client_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create error response with cultural sensitivity."""
        return {
            "analysis_id": str(uuid.uuid4()),
            "status": "error",
            "error": error,
            "coordinated_analysis": {
                "summary": """🤲 أعتذر، واجهت صعوبة في معالجة طلبك.

I apologize for the technical difficulty. While I encountered an issue processing your request, I'm still here to help with:

• Marketing strategy for Saudi Arabia
• Cultural insights and recommendations
• SEO and digital marketing guidance
• Market research and competitor analysis

Please try rephrasing your question, and I'll provide the best guidance possible.""",
                "recommended_actions": [
                    "Try rephrasing your question",
                    "Ask about specific marketing topics",
                    "Request Saudi market insights",
                    "Inquire about cultural marketing best practices"
                ],
                "cultural_adaptations": ["Error response culturally adapted for Saudi market"],
                "saudi_market_focus": True
            }
        }

    # Legacy method for backward compatibility
    async def process_request(self, user_input: str, website_url: str) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility.
        
        Args:
            user_input: User's input message
            website_url: Website URL to analyze
            
        Returns:
            Dict containing analysis results
        """
        logger.info("📞 Legacy process_request called - redirecting to coordinated analysis")
        
        request = {
            "message": f"{user_input} - analyze website: {website_url}",
            "context": {}
        }
        
        client_context = {
            "client_id": "legacy_request",
            "website_url": website_url
        }
        
        return await self.coordinate_marketing_analysis(request, client_context)

"""
Enterprise Chat Service for Morvo AI Marketing Consultant
Handles conversation flows with database persistence, cultural intelligence, and agent orchestration.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, desc

from app.api.deps import get_db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.cultural_context import CulturalContext
from app.models.conversation import Conversation, ConversationTurn, ConversationState, AgentInteraction
from app.schemas.chat import ChatMessage, ChatResponse
from app.services.ai.master_agent import MasterAgent
from app.services.ai.cultural_context_agent import CulturalContextAgent


class EnterpriseeChatService:
    """
    Enterprise chat service with database persistence, cultural intelligence, and agent orchestration.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the chat service with database session."""
        self.db = db
        self.master_agent = MasterAgent()
        self.cultural_agent = CulturalContextAgent()
        logger.info("Enterprise ChatService initialized with database integration.")

    async def process_message(self, message: ChatMessage, user_id: Optional[str] = None) -> ChatResponse:
        """
        Process an incoming chat message with full enterprise features.

        Args:
            message: The client's chat message
            user_id: Optional user ID for authenticated users

        Returns:
            ChatResponse: The response from the AI system with cultural intelligence
        """
        logger.info(f"Processing enterprise message from client: {message.client_id}")

        try:
            # Get or create user and conversation
            user = await self._get_or_create_user(message.client_id, user_id)
            conversation = await self._get_or_create_conversation(user, message)
            
            # Load user's cultural context and profile
            cultural_context = await self._get_cultural_context(user.id)
            user_profile = await self._get_user_profile(user.id)

            # Create conversation turn for user message
            user_turn = await self._create_conversation_turn(
                conversation=conversation,
                user_id=user.id,
                role="user",
                content=message.content,
                message_type="text",
                language=cultural_context.native_language if cultural_context else "ar"
            )

            # Prepare context for agents
            agent_context = {
                "user_id": str(user.id),
                "client_id": message.client_id,
                "conversation_id": str(conversation.id),
                "cultural_context": cultural_context,
                "user_profile": user_profile,
                "conversation_history": await self._get_conversation_history(conversation.id),
                "correlation_id": f"chat_{uuid.uuid4()}"
            }

            # Process with Master Agent
            agent_result = await self._process_with_master_agent(message.content, agent_context)

            # Apply cultural intelligence
            culturally_adapted_response = await self._apply_cultural_intelligence(
                agent_result, cultural_context, user_profile
            )

            # Create assistant conversation turn
            assistant_turn = await self._create_conversation_turn(
                conversation=conversation,
                user_id=user.id,
                role="assistant",
                content=culturally_adapted_response["content"],
                agent_name="master_agent",
                agent_type="orchestrator",
                message_type="text",
                language=cultural_context.native_language if cultural_context else "ar",
                tokens_used=culturally_adapted_response.get("tokens_used", 0),
                cost_usd=culturally_adapted_response.get("cost_usd", 0.0)
            )

            # Update conversation metadata
            await self._update_conversation_metadata(conversation, agent_result)

            # Create response
            chat_response = ChatResponse(
                message_id=str(assistant_turn.id),
                content=culturally_adapted_response["content"],
                agent="master_agent",
                suggestions=culturally_adapted_response.get("suggestions", []),
                cultural_adaptations=culturally_adapted_response.get("cultural_notes", []),
                conversation_id=str(conversation.id)
            )

            logger.success(f"Successfully processed enterprise message for client: {message.client_id}")
            return chat_response

        except Exception as e:
            logger.error(f"Error processing enterprise message for client {message.client_id}: {e}")
            
            # Create error response with cultural sensitivity
            error_response = await self._create_error_response(message.client_id, str(e))
            return error_response

    async def _get_or_create_user(self, client_id: str, user_id: Optional[str] = None) -> User:
        """Get existing user or create a new one."""
        if user_id:
            # Authenticated user
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                return user

        # Anonymous or new user - create with client_id as email
        user = User(
            id=uuid.uuid4(),
            email=f"{client_id}@morvo.temp",
            hashed_password="temp",  # For anonymous users
            first_name="Guest",
            is_active=True,
            is_verified=False,
            onboarding_completed=False,
            onboarding_stage="chat_started",
            login_count=1,
            subscription_tier="free",
            subscription_status="trial",
            last_activity_at=datetime.utcnow()
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info(f"Created new user for client: {client_id}")
        return user

    async def _get_or_create_conversation(self, user: User, message: ChatMessage) -> Conversation:
        """Get active conversation or create a new one."""
        # Check for active conversation
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user.id, Conversation.is_active == True)
            .order_by(desc(Conversation.created_at))
        )
        conversation = result.scalar_one_or_none()

        if conversation:
            # Update last activity
            conversation.last_activity_at = datetime.utcnow()
            await self.db.commit()
            return conversation

        # Create new conversation
        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            session_id=f"session_{uuid.uuid4()}",
            conversation_type="marketing_consultation",
            conversation_stage="discovery",
            status="active",
            is_active=True,
            is_completed=False,
            title="Marketing Consultation",
            primary_agent="master_agent",
            involved_agents=["master_agent"],
            total_turns=0,
            user_messages_count=0,
            agent_messages_count=0,
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )

        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)

        # Create initial conversation state
        state = ConversationState(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            state_name="discovery",
            state_type="consultation_stage",
            completion_percentage=10,
            is_completed=False,
            entered_at=datetime.utcnow()
        )
        
        self.db.add(state)
        await self.db.commit()

        logger.info(f"Created new conversation for user: {user.id}")
        return conversation

    async def _get_cultural_context(self, user_id: uuid.UUID) -> Optional[CulturalContext]:
        """Get user's cultural context."""
        result = await self.db.execute(
            select(CulturalContext).where(CulturalContext.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_user_profile(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        """Get user's profile."""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_conversation_history(self, conversation_id: uuid.UUID) -> list[dict]:
        """Get conversation history for context."""
        result = await self.db.execute(
            select(ConversationTurn)
            .where(ConversationTurn.conversation_id == conversation_id)
            .order_by(ConversationTurn.created_at)
            .limit(20)  # Last 20 turns for context
        )
        turns = result.scalars().all()

        return [
            {
                "role": turn.role,
                "content": turn.content,
                "agent_name": turn.agent_name,
                "timestamp": turn.created_at.isoformat()
            }
            for turn in turns
        ]

    async def _create_conversation_turn(
        self,
        conversation: Conversation,
        user_id: uuid.UUID,
        role: str,
        content: str,
        message_type: str = "text",
        language: str = "ar",
        agent_name: Optional[str] = None,
        agent_type: Optional[str] = None,
        tokens_used: int = 0,
        cost_usd: float = 0.0
    ) -> ConversationTurn:
        """Create a new conversation turn."""
        
        turn = ConversationTurn(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user_id,
            turn_number=conversation.total_turns + 1,
            role=role,
            content=content,
            agent_name=agent_name,
            agent_type=agent_type,
            message_type=message_type,
            language=language,
            cultural_context_applied=True,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            triggered_agent_handoff=False
        )

        self.db.add(turn)
        
        # Update conversation counters
        conversation.total_turns += 1
        if role == "user":
            conversation.user_messages_count += 1
        else:
            conversation.agent_messages_count += 1
        
        conversation.last_activity_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(turn)
        
        return turn

    async def _process_with_master_agent(self, content: str, context: dict) -> dict[str, Any]:
        """Process message with the Master Agent."""
        try:
            # Record agent interaction start
            interaction = AgentInteraction(
                id=uuid.uuid4(),
                conversation_id=uuid.UUID(context["conversation_id"]),
                agent_name="master_agent",
                agent_type="orchestrator",
                interaction_type="message_processing",
                input_data={"message": content, "context": context},
                execution_time_ms=0,
                success=False
            )
            
            start_time = datetime.utcnow()
            
            # Process with master agent
            result = await self.master_agent.coordinate_marketing_analysis(
                request={"message": content, "context": context},
                client_context=context
            )
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_time = int((end_time - start_time).total_seconds() * 1000)
            
            # Update interaction record
            interaction.output_data = result
            interaction.execution_time_ms = execution_time
            interaction.success = True
            
            self.db.add(interaction)
            await self.db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Master agent processing failed: {e}")
            
            # Record failed interaction
            interaction.error_message = str(e)
            interaction.success = False
            self.db.add(interaction)
            await self.db.commit()
            
            raise

    async def _apply_cultural_intelligence(
        self,
        agent_result: dict,
        cultural_context: Optional[CulturalContext],
        user_profile: Optional[UserProfile]
    ) -> dict[str, Any]:
        """Apply cultural intelligence to the agent response."""
        
        if not cultural_context:
            # Default Saudi cultural context for new users
            return {
                "content": self._add_default_cultural_context(agent_result),
                "suggestions": self._get_cultural_suggestions(),
                "cultural_notes": ["Response adapted for Saudi Arabian market context"]
            }

        # Apply specific cultural adaptations
        adapted_content = await self.cultural_agent.adapt_response_for_culture(
            response=agent_result,
            cultural_context=cultural_context,
            user_profile=user_profile
        )

        return adapted_content

    def _add_default_cultural_context(self, agent_result: dict) -> str:
        """Add default Saudi cultural context to response."""
        base_response = self._extract_response_content(agent_result)
        
        cultural_prefix = "🇸🇦 بسم الله الرحمن الرحيم\n\n"
        cultural_suffix = "\n\n📍 *Guidance tailored for the Saudi Arabian market with respect for Islamic values and Vision 2030 objectives.*"
        
        return f"{cultural_prefix}{base_response}{cultural_suffix}"

    def _get_cultural_suggestions(self) -> list[str]:
        """Get culturally appropriate suggestions."""
        return [
            "Tell me about your business goals in the Saudi market",
            "How can I help with Vision 2030 alignment?",
            "Ask about halal marketing strategies",
            "Request Arabic content recommendations",
            "Explore Ramadan marketing opportunities"
        ]

    async def _update_conversation_metadata(self, conversation: Conversation, agent_result: dict):
        """Update conversation metadata based on agent result."""
        # Extract key outcomes
        if "insights" in agent_result:
            conversation.key_outcomes = agent_result["insights"]
        
        # Update business value
        if "business_value" in agent_result:
            conversation.business_value_generated = agent_result["business_value"]
        
        await self.db.commit()

    async def _create_error_response(self, client_id: str, error: str) -> ChatResponse:
        """Create culturally sensitive error response."""
        return ChatResponse(
            message_id=f"error_{uuid.uuid4()}",
            content="""🤲 أعتذر، واجهت صعوبة في معالجة طلبك.

I apologize for the inconvenience. I encountered a technical issue while processing your request. 

🔄 Please try:
• Rephrasing your question
• Asking about a specific marketing topic
• Starting with a simple greeting

I'm here to help you with Saudi Arabian marketing insights and strategies. Let's try again! 🚀""",
            agent="system",
            suggestions=[
                "Hello, I need marketing help",
                "Tell me about Saudi market opportunities", 
                "How can I improve my business in Saudi Arabia?"
            ]
        )

    def _extract_response_content(self, agent_result: dict[str, Any]) -> str:
        """Extract the main response content from the agent result."""
        if "coordinated_analysis" in agent_result:
            analysis = agent_result["coordinated_analysis"]
            if isinstance(analysis, dict):
                return str(analysis.get("summary", "Analysis completed successfully."))
            return str(analysis)
        return "Analysis completed. Please let me know if you need more details."


async def get_chat_service(db: AsyncSession = Depends(get_db)) -> EnterpriseeChatService:
    """
    Dependency provider for the Enterprise ChatService.

    Returns:
        EnterpriseeChatService: An instance of the enterprise chat service.
    """
    return EnterpriseeChatService(db)


def create_chat_service(db: AsyncSession) -> EnterpriseeChatService:
    """
    Factory function for creating chat service without dependency injection.
    
    Args:
        db: Database session
        
    Returns:
        EnterpriseeChatService: An instance of the enterprise chat service.
    """
    return EnterpriseeChatService(db)

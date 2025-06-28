"""
Chat service for handling conversation flows with the MasterAgent.
This module defines the service responsible for processing user chat messages,
delegating them to the MasterAgent, and formatting the responses.
"""

import uuid
from typing import Any, cast

from loguru import logger

from app.agents.specialists.master_agent import MasterAgent
from app.schemas.chat import ChatMessage, ChatResponse


class ChatService:
    """
    Service for handling chat conversations and coordinating with the MasterAgent.
    """

    def __init__(self) -> None:
        """
        Initialize the chat service with a MasterAgent instance.
        """
        self.master_agent = MasterAgent()
        # Note: In a production environment, this in-memory dictionary should be
        # replaced with a persistent, scalable storage solution like Redis or a
        # database to handle conversation history across multiple service replicas.
        self.conversations: dict[str, list[dict]] = {}
        logger.info("ChatService initialized with MasterAgent.")

    async def process_message(self, message: ChatMessage) -> ChatResponse:
        """
        Process an incoming chat message by routing it to the MasterAgent.

        This method constructs a standardized request, passes it to the
        MasterAgent for orchestration, and then adapts the agent's response
        into the ChatResponse format expected by the client.

        Args:
            message: The client's chat message.

        Returns:
            ChatResponse: The response from the AI system.
        """
        logger.info(f"Processing message from client: {message.client_id}")

        if message.client_id not in self.conversations:
            self.conversations[message.client_id] = []

        self.conversations[message.client_id].append({"role": "user", "content": message.content})

        # Create a request for the MasterAgent
        request_data = {
                "message": message.content,
                "history": self.conversations[message.client_id],
            "client_id": message.client_id,
            "correlation_id": f"chat_{uuid.uuid4()}",
        }

        # Delegate the core processing to the MasterAgent
        try:
            agent_result = await self.master_agent.coordinate_marketing_analysis(
                request=request_data,
                client_context={"client_id": message.client_id},
            )

            # Extract the response from the coordinated analysis
            response_content = self._extract_response_content(agent_result)

            # Create the chat response
            chat_response = ChatResponse(
                message_id=f"msg_{uuid.uuid4()}",
                content=response_content,
                agent="master_agent",
                suggestions=self._extract_suggestions(agent_result),
            )

            # Append assistant response to conversation history
            self.conversations[message.client_id].append(
                {"role": "assistant", "content": chat_response.content}
            )

            logger.success(
                f"Successfully processed message for client: {message.client_id}"
            )
            return chat_response

        except Exception as e:
            logger.error(
                f"Error processing message for client {message.client_id}: {e}"
            )
            return ChatResponse(
                message_id=f"msg_{uuid.uuid4()}",
                content=
                    "I apologize, but I encountered an error processing your request. Please try again.",
                agent="master_agent",
                suggestions=[
                    "Try rephrasing your question",
                    "Check your internet connection",
                ],
            )

    def _extract_response_content(self, agent_result: dict[str, Any]) -> str:
        """Extract the main response content from the agent result."""
        if "coordinated_analysis" in agent_result:
            analysis = agent_result["coordinated_analysis"]
            if isinstance(analysis, dict):
                return cast(str, analysis.get("summary", "Analysis completed successfully."))
            return str(analysis)
        return "Analysis completed. Please let me know if you need more details."

    def _extract_suggestions(self, agent_result: dict[str, Any]) -> list[str]:
        """Extract suggestions from the agent result."""
        if "coordinated_analysis" in agent_result:
            analysis = agent_result["coordinated_analysis"]
            if isinstance(analysis, dict):
                return cast(list[str], analysis.get("recommended_actions", []))
        return ["Ask about specific marketing strategies", "Request competitor analysis"]


def get_chat_service() -> ChatService:
    """
    Dependency provider for the ChatService.

    This factory function is used by FastAPI's dependency injection system to
    create and provide a ChatService instance to API endpoints.

    Returns:
        ChatService: An instance of the ChatService.
    """
    return ChatService()

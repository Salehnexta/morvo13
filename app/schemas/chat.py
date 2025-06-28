"""
Enterprise Chat Schemas for Morvo AI Marketing Consultant
Supports cultural intelligence, conversation tracking, and Saudi market features.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class ChatMessage(BaseModel):
    """Enhanced chat message with cultural context support."""

    client_id: str = Field(
        description="Unique identifier for the client session",
        examples=["d290f1ee-6c54-4b01-90e6-d701748f0851"],
    )
    content: str = Field(
        description="The content of the message", 
        examples=["How can I improve my website's SEO for the Saudi market?"]
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Additional context for the message including cultural preferences"
    )
    language: Optional[str] = Field(
        default="ar", 
        description="Language preference (ar for Arabic, en for English)"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="ID of existing conversation to continue"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Authenticated user ID if available"
    )
    message_type: str = Field(
        default="text",
        description="Type of message: text, voice, image, etc."
    )
    cultural_context_required: bool = Field(
        default=True,
        description="Whether to apply Saudi cultural intelligence"
    )


class CulturalAdaptation(BaseModel):
    """Cultural adaptation information."""
    
    adaptation_type: str = Field(description="Type of cultural adaptation applied")
    reason: str = Field(description="Reason for the adaptation")
    original_content: Optional[str] = Field(default=None, description="Original content before adaptation")


class AgentMetadata(BaseModel):
    """Metadata about the agent that processed the message."""
    
    agent_name: str = Field(description="Name of the primary agent")
    agent_type: str = Field(description="Type of agent (orchestrator, specialist, etc.)")
    processing_time_ms: Optional[int] = Field(default=None, description="Processing time in milliseconds")
    tokens_used: Optional[int] = Field(default=None, description="Tokens consumed")
    cost_usd: Optional[float] = Field(default=None, description="Cost in USD")
    confidence_score: Optional[float] = Field(default=None, description="Confidence in response (0-1)")


class ChatResponse(BaseModel):
    """Enhanced response with cultural intelligence and enterprise features."""

    message_id: str = Field(
        description="Unique identifier for the message",
        examples=["msg_d290f1ee-6c54-4b01-90e6-d701748f0851"],
    )
    content: str = Field(
        description="The culturally adapted response content",
        examples=["🇸🇦 بسم الله الرحمن الرحيم\n\nBased on your website analysis for the Saudi market..."],
    )
    agent: str = Field(
        description="The primary agent that generated the response", 
        examples=["master_agent", "cultural_context_agent"]
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="ID of the conversation this message belongs to"
    )
    language: str = Field(
        default="ar",
        description="Language of the response"
    )
    
    # Cultural Intelligence Features
    cultural_adaptations: Optional[List[str]] = Field(
        default=None, 
        description="List of cultural adaptations applied"
    )
    islamic_compliance: Optional[bool] = Field(
        default=None,
        description="Whether content complies with Islamic values"
    )
    vision_2030_alignment: Optional[bool] = Field(
        default=None,
        description="Whether content aligns with Saudi Vision 2030"
    )
    
    # Enhanced Suggestions
    suggestions: Optional[List[str]] = Field(
        default=None, 
        description="Culturally appropriate follow-up suggestions"
    )
    arabic_suggestions: Optional[List[str]] = Field(
        default=None,
        description="Arabic language suggestions"
    )
    
    # Business Intelligence
    business_insights: Optional[List[str]] = Field(
        default=None,
        description="Key business insights for Saudi market"
    )
    market_opportunities: Optional[List[str]] = Field(
        default=None,
        description="Identified market opportunities"
    )
    
    # References and Sources
    references: Optional[List[Dict[str, str]]] = Field(
        default=None, 
        description="References and sources used in generating the response"
    )
    saudi_market_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Relevant Saudi market data and statistics"
    )
    
    # Agent Information
    agent_metadata: Optional[AgentMetadata] = Field(
        default=None,
        description="Metadata about agent processing"
    )
    
    # Conversation Flow
    next_recommended_action: Optional[str] = Field(
        default=None,
        description="Recommended next step in the consultation"
    )
    consultation_stage: Optional[str] = Field(
        default=None,
        description="Current stage of the marketing consultation"
    )
    
    # Timestamp
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )


class ConversationSummary(BaseModel):
    """Summary of a conversation for dashboard/analytics."""
    
    conversation_id: str = Field(description="Unique conversation identifier")
    user_id: str = Field(description="User who had the conversation")
    title: str = Field(description="Conversation title")
    stage: str = Field(description="Current consultation stage")
    total_turns: int = Field(description="Total conversation turns")
    duration_minutes: Optional[int] = Field(default=None, description="Conversation duration")
    key_insights: List[str] = Field(default=[], description="Key insights generated")
    business_value: Optional[str] = Field(default=None, description="Business value generated")
    cultural_adaptations_count: int = Field(default=0, description="Number of cultural adaptations")
    agents_involved: List[str] = Field(default=[], description="Agents that participated")
    created_at: datetime = Field(description="Conversation start time")
    last_activity: datetime = Field(description="Last activity time")


class ChatHealthCheck(BaseModel):
    """Health check response for chat system."""
    
    status: str = Field(description="System status")
    database_connected: bool = Field(description="Database connection status")
    agents_available: Dict[str, bool] = Field(description="Agent availability status")
    cultural_intelligence_active: bool = Field(description="Cultural intelligence system status")
    average_response_time_ms: Optional[float] = Field(default=None, description="Average response time")
    active_conversations: Optional[int] = Field(default=None, description="Number of active conversations")
    
    
class BulkChatRequest(BaseModel):
    """Request for processing multiple chat messages (for testing/admin)."""
    
    messages: List[ChatMessage] = Field(description="List of messages to process")
    parallel_processing: bool = Field(default=False, description="Whether to process in parallel")
    
    
class BulkChatResponse(BaseModel):
    """Response for bulk chat processing."""
    
    responses: List[ChatResponse] = Field(description="List of responses")
    processing_time_ms: int = Field(description="Total processing time")
    success_count: int = Field(description="Number of successfully processed messages")
    error_count: int = Field(description="Number of failed messages")
    errors: List[str] = Field(default=[], description="Error messages if any")

"""Enhanced Conversation models for AI Marketing Consultant System."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, JSON, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.user import User


class Conversation(Base):
    """Conversation session model for tracking complete user interactions."""
    
    __tablename__ = "conversations"

    # Primary fields
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session Information
    session_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    conversation_type: Mapped[str] = mapped_column(String(50), default="onboarding")  # onboarding, consultation, analysis, support
    conversation_stage: Mapped[str] = mapped_column(String(50), default="initial")  # initial, personal, business, analysis, complete
    
    # Conversation Status
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, paused, completed, abandoned
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_reason: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Conversation Context
    title: Mapped[Optional[str]] = mapped_column(String(200))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    primary_goal: Mapped[Optional[str]] = mapped_column(String(200))
    key_outcomes: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Agent Orchestration
    primary_agent: Mapped[str] = mapped_column(String(50), default="master_agent")
    involved_agents: Mapped[List[str]] = mapped_column(JSON, default=list)
    agent_handoffs: Mapped[Optional[List[Dict]]] = mapped_column(JSON)  # Track agent transitions
    
    # Conversation Metrics
    total_turns: Mapped[int] = mapped_column(Integer, default=0)
    user_messages_count: Mapped[int] = mapped_column(Integer, default=0)
    agent_messages_count: Mapped[int] = mapped_column(Integer, default=0)
    average_response_time: Mapped[Optional[float]] = mapped_column(Float)
    
    # Satisfaction & Quality
    user_satisfaction_score: Mapped[Optional[int]] = mapped_column(Integer)  # 1-10 scale
    conversation_quality_score: Mapped[Optional[float]] = mapped_column(Float)
    user_feedback: Mapped[Optional[str]] = mapped_column(Text)
    
    # Business Context
    business_value_generated: Mapped[Optional[str]] = mapped_column(String(100))
    actionable_insights_count: Mapped[int] = mapped_column(Integer, default=0)
    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False)
    follow_up_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Timing Information
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    conversation_turns: Mapped[List["ConversationTurn"]] = relationship(
        "ConversationTurn", back_populates="conversation", cascade="all, delete-orphan", order_by="ConversationTurn.created_at"
    )
    conversation_states: Mapped[List["ConversationState"]] = relationship(
        "ConversationState", back_populates="conversation", cascade="all, delete-orphan"
    )
    agent_interactions: Mapped[List["AgentInteraction"]] = relationship(
        "AgentInteraction", back_populates="conversation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user_id={self.user_id}, stage={self.conversation_stage})>"

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity_at = datetime.utcnow()

    def add_agent_to_conversation(self, agent_name: str) -> None:
        """Add an agent to the involved agents list."""
        if agent_name not in self.involved_agents:
            self.involved_agents.append(agent_name)

    def complete_conversation(self, reason: str = "user_completed") -> None:
        """Mark conversation as completed."""
        self.is_completed = True
        self.status = "completed"
        self.completion_reason = reason
        self.completed_at = datetime.utcnow()
        if self.started_at:
            duration = datetime.utcnow() - self.started_at
            self.duration_minutes = int(duration.total_seconds() / 60)

    def calculate_metrics(self) -> Dict:
        """Calculate conversation metrics."""
        return {
            "total_turns": self.total_turns,
            "user_messages": self.user_messages_count,
            "agent_messages": self.agent_messages_count,
            "duration_minutes": self.duration_minutes,
            "agents_involved": len(self.involved_agents),
            "satisfaction_score": self.user_satisfaction_score,
            "quality_score": self.conversation_quality_score
        }


class ConversationTurn(Base):
    """Enhanced conversation turn model with agent context and metadata."""
    
    __tablename__ = "conversation_turns"

    # Primary fields
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Turn Information
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Agent Context
    agent_name: Mapped[Optional[str]] = mapped_column(String(100))  # Which agent generated this response
    agent_type: Mapped[Optional[str]] = mapped_column(String(50))  # master, cultural, perplexity, etc.
    agent_confidence: Mapped[Optional[float]] = mapped_column(Float)  # Agent's confidence in response
    
    # Message Metadata
    message_type: Mapped[str] = mapped_column(String(50), default="text")  # text, image, file, structured_data
    language: Mapped[str] = mapped_column(String(10), default="en")  # en, ar, mixed
    cultural_context_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Processing Information
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    cost_usd: Mapped[Optional[float]] = mapped_column(Float)
    
    # External API Usage
    external_apis_used: Mapped[Optional[List[str]]] = mapped_column(JSON)  # perplexity, seranking, etc.
    api_response_data: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    # User Interaction
    user_feedback: Mapped[Optional[str]] = mapped_column(String(50))  # helpful, not_helpful, irrelevant
    user_rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5 scale
    follow_up_questions: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Conversation Flow
    triggered_agent_handoff: Mapped[bool] = mapped_column(Boolean, default=False)
    next_expected_action: Mapped[Optional[str]] = mapped_column(String(100))
    conversation_stage_transition: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Content Analysis
    intent_detected: Mapped[Optional[str]] = mapped_column(String(100))
    entities_extracted: Mapped[Optional[Dict]] = mapped_column(JSON)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversation_turns")
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="conversation_turns")

    def __repr__(self) -> str:
        return f"<ConversationTurn(id={self.id}, turn={self.turn_number}, role={self.role}, agent={self.agent_name})>"

    def is_from_agent(self) -> bool:
        """Check if this turn is from an AI agent."""
        return self.role == "assistant" and self.agent_name is not None

    def get_processing_summary(self) -> Dict:
        """Get processing summary for analytics."""
        return {
            "processing_time_ms": self.processing_time_ms,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "external_apis": self.external_apis_used or [],
            "agent_confidence": self.agent_confidence
        }


class ConversationState(Base):
    """Track conversation state transitions and user journey progress."""
    
    __tablename__ = "conversation_states"

    # Primary fields
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # State Information
    state_name: Mapped[str] = mapped_column(String(100), nullable=False)  # personal_info, business_discovery, etc.
    state_type: Mapped[str] = mapped_column(String(50), default="onboarding")  # onboarding, analysis, consultation
    previous_state: Mapped[Optional[str]] = mapped_column(String(100))
    
    # State Data
    state_data: Mapped[Optional[Dict]] = mapped_column(JSON)  # Data collected in this state
    completion_percentage: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timing
    entered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="conversation_states")

    def __repr__(self) -> str:
        return f"<ConversationState(id={self.id}, state={self.state_name}, completed={self.is_completed})>"

    def complete_state(self) -> None:
        """Mark state as completed."""
        self.is_completed = True
        self.completion_percentage = 100
        self.completed_at = datetime.utcnow()
        if self.entered_at:
            duration = datetime.utcnow() - self.entered_at
            self.duration_seconds = int(duration.total_seconds())


class AgentInteraction(Base):
    """Track individual agent interactions and performance."""
    
    __tablename__ = "agent_interactions"

    # Primary fields
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Agent Information
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    agent_version: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Interaction Context
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # query, analysis, synthesis
    input_data: Mapped[Optional[Dict]] = mapped_column(JSON)
    output_data: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    # Performance Metrics
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Resource Usage
    tokens_consumed: Mapped[Optional[int]] = mapped_column(Integer)
    api_calls_made: Mapped[Optional[int]] = mapped_column(Integer)
    cost_incurred: Mapped[Optional[float]] = mapped_column(Float)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="agent_interactions")

    def __repr__(self) -> str:
        return f"<AgentInteraction(id={self.id}, agent={self.agent_name}, type={self.interaction_type})>"

    def record_success(self, output_data: Dict, execution_time_ms: int, confidence_score: float = None) -> None:
        """Record successful agent interaction."""
        self.success = True
        self.output_data = output_data
        self.execution_time_ms = execution_time_ms
        self.confidence_score = confidence_score

    def record_failure(self, error_message: str, execution_time_ms: int = None) -> None:
        """Record failed agent interaction."""
        self.success = False
        self.error_message = error_message
        self.execution_time_ms = execution_time_ms 
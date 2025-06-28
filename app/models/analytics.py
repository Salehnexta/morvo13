"""Analytics models for tracking user performance and system metrics."""

from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, JSON, Integer, Float, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserAnalytics(Base):
    """User analytics and performance tracking."""
    
    __tablename__ = "user_analytics"

    # Primary fields
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Time Period
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    month_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Engagement Metrics
    sessions_count: Mapped[int] = mapped_column(Integer, default=0)
    total_conversation_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    messages_sent: Mapped[int] = mapped_column(Integer, default=0)
    messages_received: Mapped[int] = mapped_column(Integer, default=0)
    
    # Feature Usage
    onboarding_progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100 percentage
    agents_interacted_with: Mapped[List[str]] = mapped_column(JSON, default=list)
    features_used: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # Business Intelligence
    business_insights_generated: Mapped[int] = mapped_column(Integer, default=0)
    actionable_recommendations: Mapped[int] = mapped_column(Integer, default=0)
    marketing_strategies_created: Mapped[int] = mapped_column(Integer, default=0)
    
    # API Usage
    perplexity_api_calls: Mapped[int] = mapped_column(Integer, default=0)
    seranking_api_calls: Mapped[int] = mapped_column(Integer, default=0)
    openai_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    total_api_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    
    # User Satisfaction
    average_satisfaction_score: Mapped[Optional[float]] = mapped_column(Float)
    feedback_provided: Mapped[int] = mapped_column(Integer, default=0)
    positive_feedback_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Performance Metrics
    average_response_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    successful_interactions: Mapped[int] = mapped_column(Integer, default=0)
    failed_interactions: Mapped[int] = mapped_column(Integer, default=0)
    
    # Business Value
    estimated_time_saved_hours: Mapped[float] = mapped_column(Float, default=0.0)
    marketing_roi_improvement: Mapped[Optional[float]] = mapped_column(Float)
    cost_savings_estimated_usd: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="analytics")

    def __repr__(self) -> str:
        return f"<UserAnalytics(id={self.id}, user_id={self.user_id}, date={self.date})>"

    def calculate_engagement_score(self) -> float:
        """Calculate user engagement score (0-100)."""
        factors = [
            min(self.sessions_count * 10, 30),  # Max 30 points for sessions
            min(self.total_conversation_time_minutes / 2, 25),  # Max 25 points for time
            min(self.messages_sent * 2, 20),  # Max 20 points for messages
            min(len(self.agents_interacted_with) * 5, 15),  # Max 15 points for agent diversity
            min(self.onboarding_progress / 10, 10)  # Max 10 points for onboarding
        ]
        return min(sum(factors), 100.0)

    def get_efficiency_metrics(self) -> Dict:
        """Get efficiency metrics for the user."""
        total_interactions = self.successful_interactions + self.failed_interactions
        success_rate = (self.successful_interactions / total_interactions * 100) if total_interactions > 0 else 0
        
        return {
            "success_rate_percentage": round(success_rate, 2),
            "average_response_time_ms": self.average_response_time_ms,
            "cost_per_interaction": self.total_api_cost_usd / total_interactions if total_interactions > 0 else 0,
            "time_saved_hours": self.estimated_time_saved_hours,
            "engagement_score": self.calculate_engagement_score()
        }


class SystemMetrics(Base):
    """System-wide metrics and performance tracking."""
    
    __tablename__ = "system_metrics"

    # Primary fields
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Time Period
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hour: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-23
    
    # System Performance
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    successful_requests: Mapped[int] = mapped_column(Integer, default=0)
    failed_requests: Mapped[int] = mapped_column(Integer, default=0)
    average_response_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    
    # User Activity
    active_users: Mapped[int] = mapped_column(Integer, default=0)
    new_registrations: Mapped[int] = mapped_column(Integer, default=0)
    completed_onboardings: Mapped[int] = mapped_column(Integer, default=0)
    
    # Agent Performance
    agent_interactions: Mapped[Dict] = mapped_column(JSON, default=dict)  # agent_name -> count
    agent_success_rates: Mapped[Dict] = mapped_column(JSON, default=dict)  # agent_name -> success_rate
    agent_response_times: Mapped[Dict] = mapped_column(JSON, default=dict)  # agent_name -> avg_time_ms
    
    # External API Usage
    total_api_calls: Mapped[int] = mapped_column(Integer, default=0)
    api_costs_usd: Mapped[float] = mapped_column(Float, default=0.0)
    api_success_rates: Mapped[Dict] = mapped_column(JSON, default=dict)  # api_name -> success_rate
    
    # Business Metrics
    total_business_value_generated: Mapped[float] = mapped_column(Float, default=0.0)
    customer_satisfaction_average: Mapped[Optional[float]] = mapped_column(Float)
    revenue_impact_usd: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Error Tracking
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    critical_errors: Mapped[int] = mapped_column(Integer, default=0)
    error_types: Mapped[Dict] = mapped_column(JSON, default=dict)  # error_type -> count
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<SystemMetrics(id={self.id}, date={self.date}, hour={self.hour})>"

    def calculate_system_health_score(self) -> float:
        """Calculate overall system health score (0-100)."""
        total_requests = self.total_requests
        if total_requests == 0:
            return 100.0
        
        success_rate = (self.successful_requests / total_requests) * 100
        error_rate = (self.error_count / total_requests) * 100
        critical_error_rate = (self.critical_errors / total_requests) * 100
        
        # Weighted scoring
        health_score = (
            success_rate * 0.4 +  # 40% weight on success rate
            max(0, 100 - error_rate * 10) * 0.3 +  # 30% weight on error rate
            max(0, 100 - critical_error_rate * 20) * 0.3  # 30% weight on critical errors
        )
        
        return min(max(health_score, 0), 100)

    def get_performance_summary(self) -> Dict:
        """Get performance summary for dashboards."""
        total_requests = self.total_requests
        success_rate = (self.successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "success_rate_percentage": round(success_rate, 2),
            "average_response_time_ms": self.average_response_time_ms,
            "active_users": self.active_users,
            "system_health_score": self.calculate_system_health_score(),
            "api_costs_usd": self.api_costs_usd,
            "error_count": self.error_count
        }


class MarketingInsight(Base):
    """Marketing insights and recommendations generated by the system."""
    
    __tablename__ = "marketing_insights"

    # Primary fields
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Insight Information
    insight_type: Mapped[str] = mapped_column(String(100), nullable=False)  # competitor_analysis, market_trend, etc.
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Insight Data
    insight_data: Mapped[Dict] = mapped_column(JSON, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="medium")  # low, medium, high, critical
    
    # Source Information
    data_sources: Mapped[List[str]] = mapped_column(JSON, default=list)  # perplexity, seranking, etc.
    generated_by_agent: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Business Impact
    estimated_impact: Mapped[str] = mapped_column(String(50))  # low, medium, high
    implementation_effort: Mapped[str] = mapped_column(String(50))  # low, medium, high
    estimated_roi: Mapped[Optional[float]] = mapped_column(Float)
    
    # User Interaction
    user_rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5 scale
    user_feedback: Mapped[Optional[str]] = mapped_column(Text)
    implemented: Mapped[bool] = mapped_column(Boolean, default=False)
    implementation_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, archived, implemented
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<MarketingInsight(id={self.id}, type={self.insight_type}, priority={self.priority})>"

    def is_high_value(self) -> bool:
        """Check if this is a high-value insight."""
        return (
            self.priority in ["high", "critical"] and
            self.confidence_score >= 0.8 and
            self.estimated_impact == "high"
        )

    def get_insight_summary(self) -> Dict:
        """Get insight summary for dashboards."""
        return {
            "id": str(self.id),
            "type": self.insight_type,
            "title": self.title,
            "priority": self.priority,
            "confidence_score": self.confidence_score,
            "estimated_impact": self.estimated_impact,
            "implementation_effort": self.implementation_effort,
            "user_rating": self.user_rating,
            "implemented": self.implemented,
            "created_at": self.created_at.isoformat()
        }

    def mark_as_implemented(self) -> None:
        """Mark insight as implemented."""
        self.implemented = True
        self.implementation_date = datetime.utcnow()
        self.status = "implemented" 
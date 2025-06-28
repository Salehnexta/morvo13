"""Cultural Context model for Saudi marketing cultural intelligence."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.models import Base

if TYPE_CHECKING:
    from app.models.user import User


class CulturalContext(Base):
    """Cultural context and preferences for Saudi business environment."""
    
    __tablename__ = "cultural_contexts"

    # Primary fields
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Cultural Identity
    cultural_background: Mapped[Optional[str]] = mapped_column(String(100))  # Saudi, Gulf, Arab, International
    native_language: Mapped[str] = mapped_column(String(50), default="Arabic")
    secondary_languages: Mapped[Optional[List[str]]] = mapped_column(JSON)
    cultural_fluency_level: Mapped[str] = mapped_column(String(50), default="native")  # native, fluent, intermediate, basic
    
    # Religious Context
    religious_considerations: Mapped[bool] = mapped_column(Boolean, default=True)
    halal_marketing_required: Mapped[bool] = mapped_column(Boolean, default=True)
    prayer_time_awareness: Mapped[bool] = mapped_column(Boolean, default=True)
    ramadan_marketing_adjustments: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Regional Preferences
    primary_region: Mapped[Optional[str]] = mapped_column(String(50))  # Riyadh, Makkah, Eastern, etc.
    regional_dialect_preference: Mapped[Optional[str]] = mapped_column(String(50))
    local_market_focus: Mapped[bool] = mapped_column(Boolean, default=True)
    regional_business_customs: Mapped[Optional[Dict]] = mapped_column(JSON)
    
    # Business Culture
    business_relationship_style: Mapped[str] = mapped_column(String(50), default="relationship_first")  # relationship_first, task_first, balanced
    hierarchy_awareness: Mapped[str] = mapped_column(String(50), default="high")  # low, medium, high
    decision_making_style: Mapped[str] = mapped_column(String(50), default="consultative")  # individual, consultative, consensus
    communication_directness: Mapped[str] = mapped_column(String(50), default="indirect")  # direct, indirect, context_dependent
    
    # Family & Social Context
    family_business_consideration: Mapped[bool] = mapped_column(Boolean, default=False)
    gender_considerations: Mapped[bool] = mapped_column(Boolean, default=True)
    social_media_preferences: Mapped[Optional[List[str]]] = mapped_column(JSON)  # platforms popular in Saudi
    influencer_marketing_acceptance: Mapped[str] = mapped_column(String(50), default="moderate")  # high, moderate, low
    
    # Traditional vs Modern Balance
    traditional_values_importance: Mapped[int] = mapped_column(Integer, default=7)  # 1-10 scale
    modern_approach_openness: Mapped[int] = mapped_column(Integer, default=8)  # 1-10 scale
    innovation_acceptance: Mapped[str] = mapped_column(String(50), default="selective")  # high, selective, conservative
    
    # Vision 2030 Alignment
    vision_2030_alignment: Mapped[bool] = mapped_column(Boolean, default=True)
    sustainability_focus: Mapped[bool] = mapped_column(Boolean, default=True)
    diversification_support: Mapped[bool] = mapped_column(Boolean, default=True)
    local_content_preference: Mapped[int] = mapped_column(Integer, default=7)  # 1-10 scale
    
    # Marketing Sensitivities
    cultural_taboos_awareness: Mapped[List[str]] = mapped_column(JSON, default=list)
    preferred_imagery_style: Mapped[Optional[str]] = mapped_column(String(50))  # conservative, moderate, modern
    color_symbolism_awareness: Mapped[bool] = mapped_column(Boolean, default=True)
    text_direction_preference: Mapped[str] = mapped_column(String(10), default="rtl")  # rtl, ltr, mixed
    
    # Seasonal & Calendar Considerations
    islamic_calendar_awareness: Mapped[bool] = mapped_column(Boolean, default=True)
    national_holidays_consideration: Mapped[bool] = mapped_column(Boolean, default=True)
    seasonal_marketing_preferences: Mapped[Optional[Dict]] = mapped_column(JSON)
    cultural_events_integration: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Communication Preferences
    formal_address_preference: Mapped[bool] = mapped_column(Boolean, default=True)
    honorific_usage: Mapped[bool] = mapped_column(Boolean, default=True)
    storytelling_appreciation: Mapped[bool] = mapped_column(Boolean, default=True)
    metaphor_usage_comfort: Mapped[str] = mapped_column(String(50), default="high")  # high, medium, low
    
    # Market Understanding
    local_competitor_awareness: Mapped[bool] = mapped_column(Boolean, default=True)
    international_brand_perception: Mapped[str] = mapped_column(String(50), default="positive")  # positive, neutral, cautious
    price_sensitivity_level: Mapped[str] = mapped_column(String(50), default="medium")  # high, medium, low
    quality_vs_price_priority: Mapped[str] = mapped_column(String(50), default="quality")  # quality, price, balanced
    
    # Digital Behavior
    social_media_activity_level: Mapped[str] = mapped_column(String(50), default="high")  # high, medium, low
    e_commerce_comfort: Mapped[str] = mapped_column(String(50), default="high")  # high, medium, low
    mobile_first_preference: Mapped[bool] = mapped_column(Boolean, default=True)
    digital_payment_acceptance: Mapped[str] = mapped_column(String(50), default="high")  # high, medium, low
    
    # Custom Cultural Attributes
    custom_cultural_notes: Mapped[Optional[str]] = mapped_column(Text)
    cultural_mentor_recommendations: Mapped[Optional[List[str]]] = mapped_column(JSON)
    cultural_learning_resources: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="cultural_context")

    def __repr__(self) -> str:
        return f"<CulturalContext(id={self.id}, user_id={self.user_id}, background={self.cultural_background})>"

    def get_cultural_profile_summary(self) -> Dict:
        """Get a summary of the cultural profile for AI agents."""
        return {
            "cultural_background": self.cultural_background,
            "religious_considerations": self.religious_considerations,
            "business_style": self.business_relationship_style,
            "communication_directness": self.communication_directness,
            "traditional_modern_balance": {
                "traditional_importance": self.traditional_values_importance,
                "modern_openness": self.modern_approach_openness
            },
            "vision_2030_aligned": self.vision_2030_alignment,
            "preferred_language": self.native_language,
            "regional_focus": self.primary_region
        }

    def get_marketing_guidelines(self) -> Dict:
        """Get marketing guidelines based on cultural context."""
        guidelines = {
            "halal_compliance": self.halal_marketing_required,
            "prayer_time_consideration": self.prayer_time_awareness,
            "ramadan_adjustments": self.ramadan_marketing_adjustments,
            "cultural_taboos": self.cultural_taboos_awareness,
            "preferred_imagery": self.preferred_imagery_style,
            "formal_communication": self.formal_address_preference,
            "storytelling_approach": self.storytelling_appreciation,
            "local_content_preference": self.local_content_preference,
            "seasonal_considerations": self.seasonal_marketing_preferences or {}
        }
        return guidelines

    def is_conservative_approach_preferred(self) -> bool:
        """Check if a conservative marketing approach is preferred."""
        return (
            self.traditional_values_importance >= 7 and
            self.innovation_acceptance == "conservative" and
            self.preferred_imagery_style == "conservative"
        )

    def get_communication_style_for_agent(self) -> str:
        """Get the appropriate communication style for AI agents."""
        if self.formal_address_preference and self.honorific_usage:
            return "formal_respectful"
        elif self.communication_directness == "direct":
            return "direct_professional"
        elif self.storytelling_appreciation:
            return "narrative_engaging"
        else:
            return "professional_friendly"

    def should_use_arabic_greetings(self) -> bool:
        """Check if Arabic greetings should be used."""
        return (
            self.native_language == "Arabic" and
            self.cultural_fluency_level in ["native", "fluent"] and
            self.cultural_background in ["Saudi", "Gulf", "Arab"]
        )

    def get_regional_business_insights(self) -> Dict:
        """Get regional business insights for marketing strategies."""
        insights = {
            "region": self.primary_region,
            "local_market_focus": self.local_market_focus,
            "business_customs": self.regional_business_customs or {},
            "hierarchy_awareness": self.hierarchy_awareness,
            "decision_making_style": self.decision_making_style
        }
        return insights 
"""User Profile model for detailed user information and preferences."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.models import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserProfile(Base):
    """Detailed user profile information for personalized AI consulting."""
    
    __tablename__ = "user_profiles"

    # Primary fields
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Professional Information
    job_title: Mapped[Optional[str]] = mapped_column(String(200))
    department: Mapped[Optional[str]] = mapped_column(String(100))
    seniority_level: Mapped[Optional[str]] = mapped_column(String(50))  # entry, mid, senior, executive, c-level
    years_of_experience: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Industry & Business Context
    industry_primary: Mapped[Optional[str]] = mapped_column(String(100))
    industry_secondary: Mapped[Optional[str]] = mapped_column(String(100))
    business_model: Mapped[Optional[str]] = mapped_column(String(50))  # b2b, b2c, b2b2c, marketplace
    target_market: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Geographic Information
    country: Mapped[str] = mapped_column(String(100), default="Saudi Arabia")
    city: Mapped[Optional[str]] = mapped_column(String(100))
    region: Mapped[Optional[str]] = mapped_column(String(100))  # Riyadh, Makkah, Eastern, etc.
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Riyadh")
    
    # Communication Preferences
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")  # en, ar, mixed
    communication_style: Mapped[str] = mapped_column(String(50), default="professional")  # casual, professional, formal
    response_format_preference: Mapped[str] = mapped_column(String(50), default="detailed")  # brief, detailed, comprehensive
    
    # Marketing Experience & Goals
    marketing_experience_level: Mapped[str] = mapped_column(String(50), default="intermediate")  # beginner, intermediate, advanced, expert
    primary_marketing_goals: Mapped[Optional[List[str]]] = mapped_column(JSON)  # ["brand_awareness", "lead_generation", etc.]
    marketing_budget_range: Mapped[Optional[str]] = mapped_column(String(50))  # "under_10k", "10k_50k", etc.
    current_marketing_channels: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # AI Interaction Preferences
    preferred_agent_personality: Mapped[str] = mapped_column(String(50), default="professional_friendly")
    detail_level_preference: Mapped[str] = mapped_column(String(50), default="medium")  # low, medium, high
    explanation_style: Mapped[str] = mapped_column(String(50), default="practical")  # theoretical, practical, mixed
    
    # Learning & Development
    learning_style: Mapped[Optional[str]] = mapped_column(String(50))  # visual, auditory, kinesthetic, reading
    areas_of_interest: Mapped[Optional[List[str]]] = mapped_column(JSON)
    skill_development_goals: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Business Context
    company_size: Mapped[Optional[str]] = mapped_column(String(50))  # startup, small, medium, large, enterprise
    decision_making_authority: Mapped[Optional[str]] = mapped_column(String(50))  # influencer, decision_maker, budget_owner
    reporting_structure: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Availability & Schedule
    working_hours_start: Mapped[Optional[str]] = mapped_column(String(10))  # "09:00"
    working_hours_end: Mapped[Optional[str]] = mapped_column(String(10))  # "17:00"
    working_days: Mapped[Optional[List[str]]] = mapped_column(JSON)  # ["sunday", "monday", etc.]
    best_contact_time: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Privacy & Compliance
    data_sharing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    marketing_communications_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    analytics_consent: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Profile Completion
    profile_completion_percentage: Mapped[int] = mapped_column(Integer, default=0)
    last_profile_update: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Custom Fields for Future Extensions
    custom_attributes: Mapped[Optional[Dict]] = mapped_column(JSON)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_profile")

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, job_title={self.job_title})>"

    def calculate_profile_completion(self) -> int:
        """Calculate the profile completion percentage."""
        fields_to_check = [
            self.job_title, self.department, self.seniority_level, self.years_of_experience,
            self.industry_primary, self.business_model, self.city, self.region,
            self.marketing_experience_level, self.primary_marketing_goals,
            self.marketing_budget_range, self.current_marketing_channels,
            self.company_size, self.decision_making_authority
        ]
        
        completed_fields = sum(1 for field in fields_to_check if field is not None)
        total_fields = len(fields_to_check)
        
        percentage = int((completed_fields / total_fields) * 100)
        self.profile_completion_percentage = percentage
        return percentage

    def get_marketing_persona(self) -> str:
        """Generate a marketing persona based on profile data."""
        if not self.marketing_experience_level or not self.seniority_level:
            return "developing_marketer"
        
        if self.marketing_experience_level == "expert" and self.seniority_level in ["executive", "c-level"]:
            return "strategic_leader"
        elif self.marketing_experience_level in ["advanced", "expert"]:
            return "experienced_practitioner"
        elif self.marketing_experience_level == "intermediate":
            return "growing_professional"
        else:
            return "learning_enthusiast"

    def is_saudi_market_focused(self) -> bool:
        """Check if user is focused on Saudi market."""
        return (
            self.country == "Saudi Arabia" or
            (self.target_market and "saudi" in self.target_market.lower()) or
            (self.region is not None)
        )

    def get_preferred_communication_language(self) -> str:
        """Get the user's preferred communication language."""
        if self.preferred_language == "ar":
            return "arabic"
        elif self.preferred_language == "mixed":
            return "arabic_english_mixed"
        else:
            return "english"

    def update_profile_timestamp(self) -> None:
        """Update the last profile update timestamp."""
        self.last_profile_update = datetime.utcnow()
        self.calculate_profile_completion() 
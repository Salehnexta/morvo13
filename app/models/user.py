"""Enhanced User model for the AI Marketing Consultant System."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.business_profile import BusinessProfile
    from app.models.seranking import SERankingBacklinkAnalysis, SERankingDomain
    from app.models.conversation import ConversationTurn, Conversation
    from app.models.user_profile import UserProfile
    from app.models.cultural_context import CulturalContext
    from app.models.analytics import UserAnalytics


class User(Base):
    """Enhanced User model with enterprise features for AI Marketing Consultant."""
    
    __tablename__ = "users"

    # Primary fields
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Profile fields
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    title: Mapped[Optional[str]] = mapped_column(String(50))  # Dr., Mr., Eng., etc.
    preferred_name: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)  # Admin access
    
    # Onboarding tracking
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    onboarding_stage: Mapped[Optional[str]] = mapped_column(String(50))  # personal, business, analysis, complete
    onboarding_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # System tracking
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    login_count: Mapped[int] = mapped_column(default=0)
    
    # Subscription and billing
    subscription_tier: Mapped[str] = mapped_column(String(50), default="free")  # free, basic, professional, enterprise
    subscription_status: Mapped[str] = mapped_column(String(50), default="active")  # active, suspended, cancelled
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    deleted_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))

    # Relationships with string references to avoid circular imports
    user_profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    cultural_context: Mapped[Optional["CulturalContext"]] = relationship(
        "CulturalContext", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    business_profiles: Mapped[List["BusinessProfile"]] = relationship(
        "BusinessProfile", back_populates="user", cascade="all, delete-orphan"
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    conversation_turns: Mapped[List["ConversationTurn"]] = relationship(
        "ConversationTurn", back_populates="user", cascade="all, delete-orphan"
    )
    seranking_domains: Mapped[List["SERankingDomain"]] = relationship(
        "SERankingDomain", back_populates="user", cascade="all, delete-orphan"
    )
    seranking_backlink_analyses: Mapped[List["SERankingBacklinkAnalysis"]] = relationship(
        "SERankingBacklinkAnalysis", back_populates="user", cascade="all, delete-orphan"
    )
    analytics: Mapped[List["UserAnalytics"]] = relationship(
        "UserAnalytics", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.preferred_name or self.first_name})>"

    @property
    def full_name(self) -> str:
        """Get the user's full name with title."""
        parts = []
        if self.title:
            parts.append(self.title)
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else self.email

    @property
    def display_name(self) -> str:
        """Get the user's preferred display name."""
        if self.preferred_name:
            return f"{self.title} {self.preferred_name}" if self.title else self.preferred_name
        return self.full_name

    def is_onboarding_complete(self) -> bool:
        """Check if user has completed onboarding."""
        return self.onboarding_completed and self.onboarding_stage == "complete"

    def update_last_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity_at = datetime.utcnow()

    def increment_login_count(self) -> None:
        """Increment login count and update last login."""
        self.login_count += 1
        self.last_login_at = datetime.utcnow()
        self.update_last_activity()

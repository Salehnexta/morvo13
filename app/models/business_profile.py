"""
Business profile models for the marketing platform.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.user import User


class BusinessProfile(Base):
    """
    Business profile model for storing customer information.

    This serves as the core data model for customer information in the platform.
    """

    __tablename__ = "business_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Basic business information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[str | None] = mapped_column(String(500))
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    company_size: Mapped[str] = mapped_column(String(50), nullable=False)
    locations: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Marketing information
    target_audience: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    marketing_goals: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    competitors: Mapped[List[str] | None] = mapped_column(JSON)
    current_channels: Mapped[List[str] | None] = mapped_column(JSON)
    pain_points: Mapped[List[str] | None] = mapped_column(JSON)

    # Social media profiles
    social_profiles: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # Analytics and tracking
    analytics_connected: Mapped[bool] = mapped_column(Boolean, default=False)

    # Brand and voice
    brand_voice: Mapped[str | None] = mapped_column(String(100))
    brand_values: Mapped[List[str] | None] = mapped_column(JSON)
    usp: Mapped[str | None] = mapped_column(Text)  # Unique Selling Proposition

    # Content preferences
    content_preferences: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # Automation preferences
    automation_level: Mapped[str] = mapped_column(String(50), default="balanced")  # conservative, balanced, aggressive

    # Subscription and onboarding
    subscription_tier: Mapped[str] = mapped_column(String(50), default="free")  # free, basic, premium, enterprise
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="business_profiles")

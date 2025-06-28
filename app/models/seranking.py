"""SE Ranking models for SEO data tracking."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.user import User


class SERankingDomain(Base):
    __tablename__ = "seranking_domains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    domain_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # SE Ranking specific data
    project_id: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)

    # Analysis metadata
    last_analysis_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    analysis_status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending, processing, completed, failed

    # SEO metrics
    organic_keywords_count: Mapped[int] = mapped_column(Integer, default=0)
    total_backlinks: Mapped[int] = mapped_column(Integer, default=0)
    domain_authority: Mapped[int] = mapped_column(Integer, default=0)

    # Tracking data (JSON for flexibility)
    keyword_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    competitor_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    ranking_history: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="seranking_domains")


class SERankingBacklinkAnalysis(Base):
    __tablename__ = "seranking_backlink_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    domain_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("seranking_domains.id"), nullable=False)

    # Analysis details
    analysis_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    total_backlinks: Mapped[int] = mapped_column(Integer, default=0)
    referring_domains: Mapped[int] = mapped_column(Integer, default=0)

    # Quality metrics
    high_quality_links: Mapped[int] = mapped_column(Integer, default=0)
    medium_quality_links: Mapped[int] = mapped_column(Integer, default=0)
    low_quality_links: Mapped[int] = mapped_column(Integer, default=0)

    # Detailed analysis data
    backlink_details: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    anchor_text_analysis: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    link_velocity: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)

    # Analysis notes and recommendations
    analysis_notes: Mapped[str | None] = mapped_column(Text)
    recommendations: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="seranking_backlink_analyses")
    domain: Mapped["SERankingDomain"] = relationship("SERankingDomain")

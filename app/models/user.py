"""User model for the application."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.business_profile import BusinessProfile
    from app.models.seranking import SERankingBacklinkAnalysis, SERankingDomain


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships with string references to avoid circular imports
    business_profiles: Mapped[List["BusinessProfile"]] = relationship("BusinessProfile", back_populates="user")
    seranking_domains: Mapped[List["SERankingDomain"]] = relationship("SERankingDomain", back_populates="user")
    seranking_backlink_analyses: Mapped[List["SERankingBacklinkAnalysis"]] = relationship(
        "SERankingBacklinkAnalysis", back_populates="user"
    )

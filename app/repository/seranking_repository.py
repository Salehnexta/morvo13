from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseError
from app.models.seranking import (
    SERankingBacklinkAnalysis,
    SERankingDomain,
)


class SERankingRepository:
    """Handles database operations for SE Ranking data using async SQLAlchemy."""

    def __init__(self, db: AsyncSession) -> None:
        """Initializes the SERankingRepository with an async SQLAlchemy session."""
        self.db = db

    async def create_domain(self, domain_data: dict[str, Any]) -> SERankingDomain:
        """Creates a new SERankingDomain record."""
        try:
            domain = SERankingDomain(**domain_data)
            self.db.add(domain)
            await self.db.commit()
            await self.db.refresh(domain)
            return domain
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error creating domain: {e}") from e

    async def get_domain_by_name(self, domain_name: str) -> SERankingDomain | None:
        """Retrieves a SERankingDomain by its name."""
        result = await self.db.execute(
            select(SERankingDomain).where(SERankingDomain.domain_name == domain_name)
        )
        return result.scalar_one_or_none()

    async def update_domain_status(
        self, domain_id: UUID, status: str, last_analyzed: datetime | None = None
    ) -> None:
        """Updates the analysis status of a SERankingDomain."""
        try:
            result = await self.db.execute(
                select(SERankingDomain).where(SERankingDomain.id == domain_id)
            )
            domain = result.scalar_one_or_none()
            if domain:
                domain.analysis_status = status
                if last_analyzed:
                    domain.last_analysis_date = last_analyzed
                await self.db.commit()
                await self.db.refresh(domain)
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error updating domain status: {e}") from e

    async def create_backlink_analysis(
        self, analysis_data: dict[str, Any]
    ) -> SERankingBacklinkAnalysis:
        """Creates a new SERankingBacklinkAnalysis record."""
        try:
            analysis = SERankingBacklinkAnalysis(**analysis_data)
            self.db.add(analysis)
            await self.db.commit()
            await self.db.refresh(analysis)
            return analysis
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error creating backlink analysis: {e}") from e

    async def get_domain_analysis_history(self, domain: str) -> list[SERankingBacklinkAnalysis]:
        """Gets the analysis history for a specific domain."""
        try:
            stmt = (
                select(SERankingBacklinkAnalysis)
                .join(SERankingDomain)
                .where(SERankingDomain.domain_name == domain)
                .order_by(SERankingBacklinkAnalysis.created_at.desc())
            )
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseError(f"Error retrieving domain analysis history: {e}") from e

    async def get_user_domains(self, user_id: UUID) -> list[SERankingDomain]:
        """Gets all domains for a specific user."""
        try:
            result = await self.db.execute(
                select(SERankingDomain).where(SERankingDomain.user_id == user_id)
            )
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseError(f"Error retrieving user domains: {e}") from e

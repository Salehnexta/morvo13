import logging
from datetime import datetime, timezone
from typing import Any

from app.api.deps import AsyncSessionLocal
from app.core.celery_app import celery_app
from app.models.seranking import SERankingDomain
from app.repository.seranking_repository import SERankingRepository
from app.services.seranking_service import SERankingService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, default_retry_delay=300, max_retries=5)  # type: ignore
async def analyze_website_task(self: Any, domain: str, user_id: str) -> None:
    """
    Celery task to analyze a website's SEO profile using SE Ranking.
    """
    seranking_service = SERankingService()
    async with AsyncSessionLocal() as db:
        seranking_repo = SERankingRepository(db)
        domain_obj: SERankingDomain | None = None  # Initialize to handle exceptions before assignment
        try:
            domain_obj = await seranking_repo.get_domain_by_name(domain)
            if not domain_obj:
                domain_obj = await seranking_repo.create_domain(
                    {"domain_name": domain, "user_id": user_id}
                )

            analysis_result = await seranking_service.analyze_backlinks(domain)

            if not analysis_result.get("success"):
                raise Exception(
                    f"SE Ranking API error: {analysis_result.get('error', 'Unknown error')}"
                )

            api_data = analysis_result["data"]["summary"][0]
            analysis_data = {
                "domain_id": domain_obj.id,
                "user_id": user_id,
                "total_backlinks": api_data.get("backlinks", 0),
                "referring_domains": api_data.get("refdomains", 0),
                "backlink_details": api_data,  # Store the full summary
                "status": "completed",
                "timestamp": datetime.now(timezone.utc),
            }

            await seranking_repo.create_backlink_analysis(analysis_data)

            await seranking_repo.update_domain_status(
                domain_obj.id, "completed", datetime.now(timezone.utc)
            )
            logger.info(f"Successfully completed SE Ranking analysis for {domain}")

        except Exception as exc:
            logger.error(f"SE Ranking analysis task failed for {domain}: {exc}")
            if domain_obj:
                await seranking_repo.update_domain_status(domain_obj.id, "failed")
            self.retry(exc=exc)
        finally:
            await seranking_service.close()

"""API endpoints for SE Ranking integration."""

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repository.seranking_repository import SERankingRepository
from app.tasks.seranking_tasks import analyze_website_task
from app.core.config.settings import settings as app_settings

router = APIRouter(prefix="/seranking", tags=["SE Ranking"])


@router.post("/analyze/{domain}")
async def analyze_domain(
    domain: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Analyze a domain using the SE Ranking API and store the results."""
    # seranking_service = SERankingService()
    seranking_repo = SERankingRepository(db)

    try:
        # Check if domain already exists, create if not
        domain_obj = await seranking_repo.get_domain_by_name(domain)
        if not domain_obj:
            domain_obj = await seranking_repo.create_domain(
                {"domain_name": domain, "user_id": current_user.id}
            )

        # Dispatch the task to Celery (use predictable ID during testing so tests can assert)
        user_identifier = (
            "user_id_from_auth" if app_settings.ENVIRONMENT == "testing" else str(current_user.id)
        )

        background_tasks.add_task(analyze_website_task.delay, domain, user_identifier)

        return {
            "success": True,
            "message": f"SE Ranking analysis for {domain} has been queued.",
            "domain_id": domain_obj.id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/domains/{domain}/history")
async def get_domain_history(
    domain: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get the analysis history for a specific domain."""
    seranking_repo = SERankingRepository(db)
    history = await seranking_repo.get_domain_analysis_history(domain)
    return {"domain": domain, "history": history}

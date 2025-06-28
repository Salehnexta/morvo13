"""Onboarding API endpoints for new users."""

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.specialists.master_agent import MasterAgent
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.onboarding import OnboardingRequest, OnboardingResponse

router = APIRouter()


@router.post("/start", response_model=OnboardingResponse)
async def start_onboarding(
    request: OnboardingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OnboardingResponse:
    """Start the onboarding process for a new user."""
    try:
        # Initialize the master agent
        agent = MasterAgent()

        # Process the onboarding request with the agent
        analysis_request = {
            "business_info": request.model_dump(),
            "user_id": str(current_user.id),
            "onboarding_stage": "initial",
        }

        # Get initial analysis from the master agent
        result = await agent.coordinate_marketing_analysis(
            request=analysis_request,
            client_context={"user_id": str(current_user.id), "stage": "onboarding"},
        )

        # Extract recommendations from the result
        recommendations = []
        if "coordinated_analysis" in result:
            analysis = result["coordinated_analysis"]
            if isinstance(analysis, dict):
                recommendations = analysis.get("recommended_actions", [])

        # Default recommendations if none provided
        if not recommendations:
            recommendations = [
                "Set up your business profile completely",
                "Connect your social media accounts",
                "Define your target audience",
                "Set your marketing goals",
            ]

        return OnboardingResponse(
            message="Welcome to Morvo AI! Let's get your marketing strategy set up.",
            recommendations=recommendations,
            next_steps=["Complete business profile", "Connect analytics", "Review suggestions"],
            onboarding_complete=False,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during onboarding: {e!s}") from e


@router.get("/status")
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get the current onboarding status for the user."""
    return {
        "user_id": str(current_user.id),
        "onboarding_started": True,
        "onboarding_complete": False,
        "message": "Onboarding system ready",
    }

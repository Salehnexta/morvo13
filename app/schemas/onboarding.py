"""
Pydantic schemas for the session-based, multi-step onboarding flow.

These models define the data contracts for starting a session, submitting
steps, and finalizing the process to trigger the asynchronous enrichment.
"""

from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class OnboardingRequest(BaseModel):
    """Request to start the onboarding process."""

    business_name: str = Field(description="Name of the business")
    industry: str = Field(description="Industry/sector of the business")
    website: str | None = Field(None, description="Business website URL")
    target_market: str = Field(description="Primary target market")
    marketing_goals: list[str] = Field(description="List of marketing goals")
    current_channels: list[str] = Field(default=[], description="Current marketing channels")


class OnboardingResponse(BaseModel):
    """Response from the onboarding process."""

    message: str = Field(description="Welcome message")
    recommendations: list[str] = Field(description="Initial recommendations")
    next_steps: list[str] = Field(description="Suggested next steps")
    onboarding_complete: bool = Field(description="Whether onboarding is complete")


class OnboardingStartRequest(BaseModel):
    """Request to initiate a new onboarding session."""

    # In a real multi-tenant system, we might include a user_id or org_id here.
    client_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the client initiating the session.",
    )


class OnboardingStartResponse(BaseModel):
    """Response containing the newly created session ID."""

    session_id: UUID = Field(description="The unique identifier for this onboarding session.")
    message: str = Field(
        default="Onboarding session started successfully.", description="A confirmation message."
    )


class OnboardingStepRequest(BaseModel):
    """Request to submit data for a single step in the onboarding flow."""

    session_id: UUID = Field(description="The active onboarding session ID.")
    step_name: str = Field(description="The name of the step being submitted (e.g., 'basic_info').")
    step_data: dict[str, Any] = Field(
        description="A dictionary containing the data for this specific step."
    )


class OnboardingStepResponse(BaseModel):
    """Response confirming that a step has been successfully processed."""

    session_id: UUID = Field(description="The active onboarding session ID.")
    status: str = Field(default="step_saved", description="The status of the step submission.")
    message: str = Field(description="A confirmation message for the submitted step.")


class OnboardingFinalizeRequest(BaseModel):
    """Request to finalize the onboarding process and trigger enrichment."""

    session_id: UUID = Field(description="The session ID to finalize.")


class OnboardingFinalizeResponse(BaseModel):
    """
    Response confirming that the enrichment process has been triggered.

    Note: This response is returned immediately, while the actual enrichment
    runs as a background task.
    """

    session_id: UUID = Field(description="The session ID that was finalized.")
    status: str = Field(
        default="enrichment_triggered",
        description="Confirms that the background analysis has started.",
    )
    message: str = Field(
        default="Onboarding finalized. AI analysis is now running in the background.",
        description="A confirmation message.",
    )

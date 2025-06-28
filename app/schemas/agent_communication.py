"""
Schemas for standardized agent-to-agent (A2A) communication.

This module defines the data contracts for requests and responses within the
agent network, ensuring consistency, validation, and clear tracing capabilities
as per enterprise standards.
"""

from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Status(str, Enum):
    """Enumeration for the status of an agent task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRequest(BaseModel):
    """
    Standard request model for all inter-agent communication.

    Attributes:
        task_type: Defines the specific operation the receiving agent should perform.
        payload: Contains the necessary data for the agent to execute the task.
        context: Provides shared context, such as user info or conversation history.
        client_id: Uniquely identifies the end-user's session.
        correlation_id: A unique ID for tracing a single logical request across the
                        entire distributed agent network.
    """

    task_type: str = Field(description="The type of task for the agent to perform.")
    payload: dict[str, Any] = Field(
        default_factory=dict, description="The data required to perform the task."
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Shared context, like user preferences or conversation history.",
    )
    client_id: UUID = Field(description="Unique identifier for the client session.")
    correlation_id: UUID = Field(
        default_factory=uuid4, description="Unique ID for tracing a request across multiple agents."
    )


class AgentResponse(BaseModel):
    """
    Standard response model for all inter-agent communication.

    Attributes:
        status: The final status of the requested task.
        message: A human-readable summary of the outcome.
        payload: The resulting data or output from the agent's task.
        correlation_id: The correlation ID from the original request for tracing.
    """

    status: Status = Field(description="The final status of the task.")
    message: str = Field(description="A human-readable message about the outcome.")
    payload: dict[str, Any] = Field(
        default_factory=dict, description="The output data from the task."
    )
    correlation_id: UUID = Field(description="The correlation ID from the original request.")

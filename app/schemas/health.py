"""
Schemas related to health check endpoint.
"""


from pydantic import BaseModel, Field


class AgentInfo(BaseModel):
    """Information about an agent."""
    name: str = Field(description="Name of the agent")
    status: str = Field(description="Current status of the agent")
    type: str = Field(description="Type/category of the agent")


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(description="Status of the API: 'ok' if healthy", examples=["ok"])
    version: str = Field(description="API version", examples=["1.0.0"])
    environment: str | None = Field(default=None, description="Current environment")
    agents: list[AgentInfo] | None = Field(default=None, description="List of active agents")
    websocket_connections: int | None = Field(default=None, description="Number of active WebSocket connections")
    protocols_enhanced: bool | None = Field(default=None, description="Whether protocols are enhanced")
    database_connected: bool | None = Field(default=None, description="Database connection status")
    services: dict[str, str] | None = Field(default=None, description="Status of various services")

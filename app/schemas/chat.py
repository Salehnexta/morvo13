"""
Schemas related to chat functionality.
"""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message sent by the client."""

    client_id: str = Field(
        description="Unique identifier for the client session",
        examples=["d290f1ee-6c54-4b01-90e6-d701748f0851"],
    )
    content: str = Field(
        description="The content of the message", examples=["How can I improve my website's SEO?"]
    )
    context: dict[str, str] | None = Field(
        default=None, description="Additional context for the message"
    )


class ChatResponse(BaseModel):
    """Response to a chat message."""

    message_id: str = Field(
        description="Unique identifier for the message",
        examples=["msg_d290f1ee-6c54-4b01-90e6-d701748f0851"],
    )
    content: str = Field(
        description="The content of the response",
        examples=["Based on your website analysis, here are 3 SEO improvements..."],
    )
    agent: str = Field(
        description="The agent that generated the response", examples=["master_agent", "seo_agent"]
    )
    references: list[dict[str, str]] | None = Field(
        default=None, description="References and sources used in generating the response"
    )
    suggestions: list[str] | None = Field(
        default=None, description="Suggested follow-up queries or actions"
    )

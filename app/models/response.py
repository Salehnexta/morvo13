"""Pydantic models for API responses."""

from pydantic import BaseModel


class ChatResponse(BaseModel):
    """Model for chat responses."""

    message: str

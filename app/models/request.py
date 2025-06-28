"""Pydantic models for API requests."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Model for chat requests."""

    message: str

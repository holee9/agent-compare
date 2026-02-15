"""
Data models for gateway module.
"""

from typing import Any

from pydantic import BaseModel, Field


class GatewayRequest(BaseModel):
    """Request to send to AI provider."""

    task_name: str
    prompt: str
    max_tokens: int | None = None
    timeout: int = 120


class GatewayResponse(BaseModel):
    """Response from AI provider."""

    content: str
    success: bool
    error: str | None = None
    tokens_used: int = 0
    response_time: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)

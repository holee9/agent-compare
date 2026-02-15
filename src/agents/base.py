"""
Base agent protocol and utilities.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from src.core.exceptions import AgentException, ErrorCode
from src.gateway.models import GatewayRequest, GatewayResponse


class AgentType(str, Enum):
    """Supported AI agent types."""

    CHATGPT = "chatgpt"
    CLAUDE = "claude"
    GEMINI = "gemini"
    PERPLEXITY = "perplexity"


class AgentRequest(BaseModel):
    """Request to send to AI agent."""

    task_name: str
    prompt: str
    max_tokens: int | None = None
    timeout: int = 120


class AgentResponse(BaseModel):
    """Response from AI agent."""

    agent_name: AgentType
    task_name: str
    content: str
    tokens_used: int = 0
    response_time: float = 0.0
    success: bool = True
    error: str | None = None


class AsyncAgent(ABC):
    """
    Abstract base class for all AI agents.

    Wraps gateway provider and adds agent-specific logic.
    """

    def __init__(self, gateway_provider) -> None:
        """Initialize agent with gateway provider."""
        self.gateway = gateway_provider

    @abstractmethod
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute agent task.

        Args:
            request: AgentRequest with task_name and prompt

        Returns:
            AgentResponse with AI response
        """
        raise NotImplementedError

    async def validate_response(self, response: GatewayResponse) -> AgentResponse:
        """
        Validate and normalize gateway response.

        Args:
            response: Raw GatewayResponse

        Returns:
            AgentResponse with agent metadata
        """
        # Validate response
        if not response.success:
            return AgentResponse(
                agent_name=self.gateway.__class__.__name__,
                task_name="unknown",
                content="",
                success=False,
                error=response.error or "Gateway returned failure",
            )

        # Convert to AgentResponse
        return AgentResponse(
            agent_name=self.gateway.__class__.__name__,
            task_name="unknown",  # Will be updated by caller
            content=response.content,
            tokens_used=response.tokens_used,
            response_time=response.response_time,
            success=response.success,
            error=response.error,
        )

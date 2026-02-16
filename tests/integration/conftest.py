"""
Shared fixtures and configuration for integration tests.

This module provides:
- Mock AI provider responses
- Fault injection capabilities
- Test data fixtures
- Common test utilities
"""

import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.models import AgentType
from src.gateway.base import GatewayRequest, GatewayResponse


@pytest.fixture
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def fixtures_dir(project_root: Path) -> Path:
    """Get the test fixtures directory."""
    return project_root / "tests" / "integration" / "fixtures"


@pytest.fixture
def scenarios_dir(project_root: Path) -> Path:
    """Get the test scenarios directory."""
    return project_root / "tests" / "integration" / "scenarios"


@pytest.fixture
def mock_gateway_response():
    """Factory for creating mock GatewayResponse objects."""

    def _create(
        success: bool = True,
        content: str = "Mock response",
        error: str | None = None,
        tokens_used: int = 100,
        response_time: float = 1.5,
    ) -> GatewayResponse:
        return GatewayResponse(
            content=content,
            success=success,
            error=error,
            tokens_used=tokens_used,
            response_time=response_time,
            metadata={},
        )

    return _create


@pytest.fixture
def mock_gateway_request():
    """Factory for creating mock GatewayRequest objects."""

    def _create(
        task_name: str = "test_task",
        prompt: str = "Test prompt",
        max_tokens: int | None = None,
        timeout: int = 120,
    ) -> GatewayRequest:
        return GatewayRequest(
            task_name=task_name,
            prompt=prompt,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    return _create


@pytest.fixture
def fault_injector():
    """
    Fault injector for simulating various failure modes in AI providers.

    Usage:
        injector = fault_injector()
        injector.set_timeout("claude")  # Claude will timeout
        injector.set_error("gemini", 500)  # Gemini returns 500 error
        injector.set_rate_limit("chatgpt")  # ChatGPT rate limited
    """

    class FaultInjector:
        """Controls fault injection for testing."""

        def __init__(self) -> None:
            self._timeouts: set[str] = set()
            self._errors: dict[str, int] = {}
            self._rate_limits: set[str] = set()
            self._network_errors: set[str] = set()
            self._malformed_responses: set[str] = set()

        def set_timeout(self, provider: str) -> None:
            """Make provider timeout on next request."""
            self._timeouts.add(provider)

        def set_error(self, provider: str, error_code: int) -> None:
            """Make provider return HTTP error code."""
            self._errors[provider] = error_code

        def set_rate_limit(self, provider: str) -> None:
            """Make provider return rate limit response."""
            self._rate_limits.add(provider)

        def set_network_error(self, provider: str) -> None:
            """Make provider raise connection error."""
            self._network_errors.add(provider)

        def set_malformed_response(self, provider: str) -> None:
            """Make provider return malformed response."""
            self._malformed_responses.add(provider)

        def clear_all(self) -> None:
            """Clear all fault settings."""
            self._timeouts.clear()
            self._errors.clear()
            self._rate_limits.clear()
            self._network_errors.clear()
            self._malformed_responses.clear()

        def has_fault(self, provider: str) -> bool:
            """Check if provider has any fault configured."""
            return (
                provider in self._timeouts
                or provider in self._errors
                or provider in self._rate_limits
                or provider in self._network_errors
                or provider in self._malformed_responses
            )

        def get_fault(self, provider: str) -> str | None:
            """Get the fault type for a provider."""
            if provider in self._timeouts:
                return "timeout"
            if provider in self._errors:
                return f"error_{self._errors[provider]}"
            if provider in self._rate_limits:
                return "rate_limit"
            if provider in self._network_errors:
                return "network_error"
            if provider in self._malformed_responses:
                return "malformed"
            return None

    return FaultInjector()


@pytest.fixture
def mock_provider_factory(mock_gateway_response):
    """
    Factory for creating mock AI providers with controllable responses.

    Usage:
        factory = mock_provider_factory()
        claude = factory.create("claude", success=True, content="Response")
        failing_gemini = factory.create("gemini", success=False, error="Timeout")
    """

    class MockProviderFactory:
        """Creates mock provider instances for testing."""

        def __init__(self, response_factory) -> None:
            self.response_factory = response_factory
            self._call_count: dict[str, int] = {}

        def create(
            self,
            provider_name: str,
            success: bool = True,
            content: str = "Mock response",
            error: str | None = None,
            agent_type: AgentType = AgentType.CLAUDE,
        ) -> MagicMock:
            """Create a mock provider instance."""
            provider = MagicMock()
            provider.provider_name = provider_name
            provider.agent_type = agent_type

            # Create async mock for send_message
            async def mock_send(request: GatewayRequest) -> GatewayResponse:
                self._call_count[provider_name] = self._call_count.get(provider_name, 0) + 1
                return self.response_factory(
                    success=success,
                    content=content,
                    error=error,
                )

            provider.send_message = mock_send
            provider.check_session = AsyncMock(return_value=True)
            provider.login_flow = AsyncMock()
            provider.save_session = MagicMock()
            provider.load_session = MagicMock(return_value=True)

            return provider

        def get_call_count(self, provider_name: str) -> int:
            """Get number of times a provider was called."""
            return self._call_count.get(provider_name, 0)

        def reset_call_counts(self) -> None:
            """Reset all call counts."""
            self._call_count.clear()

    return MockProviderFactory(mock_gateway_response)


@pytest.fixture
def provider_selector_map():
    """Get the default provider fallback order."""
    return ["claude", "gemini", "chatgpt", "perplexity"]


@pytest.fixture
def mock_pipeline_state():
    """Create a mock pipeline state for testing."""

    class MockPipelineState:
        """Mock pipeline state for testing."""

        def __init__(self) -> None:
            self.current_phase = "phase1"
            self.completed_phases: list[str] = []
            self.results: dict[str, Any] = {}
            self.errors: list[dict[str, Any]] = []
            self.fallback_events: list[dict[str, Any]] = []

        def add_fallback_event(
            self,
            from_provider: str,
            to_provider: str,
            reason: str,
        ) -> None:
            """Record a fallback event."""
            self.fallback_events.append({
                "from": from_provider,
                "to": to_provider,
                "reason": reason,
            })

        def add_error(self, phase: str, provider: str, error: str) -> None:
            """Record an error."""
            self.errors.append({
                "phase": phase,
                "provider": provider,
                "error": error,
            })

        def complete_phase(self, phase: str, result: Any) -> None:
            """Mark a phase as completed."""
            self.completed_phases.append(phase)
            self.results[phase] = result

    return MockPipelineState()


@pytest.fixture
def sample_prompts(fixtures_dir: Path):
    """Load sample prompts for testing."""
    return {
        "simple": "What is the capital of France?",
        "complex": "Analyze the impact of climate change on global agriculture.",
        "multi_step": "Research AI trends and create a strategic plan.",
    }


@pytest.fixture
def sample_responses(fixtures_dir: Path):
    """Load sample AI responses for testing."""
    return {
        "claude": {
            "success": "Based on my analysis, here are the key findings...",
            "timeout": None,
            "error": "I apologize, but I'm unable to complete this request.",
        },
        "gemini": {
            "success": "Here's what I found on this topic...",
            "timeout": None,
            "error": "I couldn't process that request.",
        },
        "chatgpt": {
            "success": "Let me help you with that...",
            "timeout": None,
            "error": "Sorry, I can't assist with this.",
        },
    }


@pytest.fixture
def timeout_config():
    """Default timeout configuration for testing."""
    return {
        "request_timeout": 120,
        "max_retries": 2,
        "retry_delay": 1.0,
        "circuit_breaker_threshold": 3,
        "circuit_breaker_timeout": 60,
    }


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

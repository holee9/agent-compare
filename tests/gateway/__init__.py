"""
Tests for gateway package.
"""

import pytest

from src.gateway import __all__


def test_base_provider_defined():
    """Test that BaseProvider is defined."""
    from src.gateway.base import BaseProvider
    assert BaseProvider is not None


def test_chatgpt_provider_defined():
    """Test that ChatGPTProvider is defined."""
    from src.gateway.chatgpt_provider import ChatGPTProvider
    assert ChatGPTProvider is not None


def test_claude_provider_defined():
    """Test that ClaudeProvider is defined."""
    from src.gateway.claude_provider import ClaudeProvider
    assert ClaudeProvider is not None


def test_gemini_provider_defined():
    """Test that GeminiProvider is defined."""
    from src.gateway.gemini_provider import GeminiProvider
    assert GeminiProvider is not None


def test_perplexity_provider_defined():
    """Test that PerplexityProvider is defined."""
    from src.gateway.perplexity_provider import PerplexityProvider
    assert PerplexityProvider is not None


def test_session_manager_defined():
    """Test that SessionManager is defined."""
    from src.gateway.session import SessionManager
    assert SessionManager is not None


def test_gateway_models_defined():
    """Test that gateway models are defined."""
    from src.gateway.models import GatewayRequest, GatewayResponse
    assert GatewayRequest is not None
    assert GatewayResponse is not None

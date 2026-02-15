"""
Tests for agent layer.
"""

import pytest

from src.agents.base import AsyncAgent
from src.agents.router import AgentRouter, AgentMapping, PhaseTask
from src.agents.chatgpt_agent import ChatGPTAgent
from src.agents.claude_agent import ClaudeAgent
from src.agents.gemini_agent import GeminiAgent
from src.agents.perplexity_agent import PerplexityAgent


class TestAsyncAgent:
    """Tests for AsyncAgent interface."""

    def test_cannot_instantiate(self):
        """AsyncAgent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AsyncAgent(gateway_provider="dummy")


class TestAgentRouter:
    """Tests for AgentRouter."""

    def test_init(self):
        """Test router initialization."""
        router = AgentRouter(settings=None)
        assert router is not None

    def test_get_default_mapping(self):
        """Test default agent mapping."""
        from src.agents.router import AgentMapping

        mapping = AgentMapping.get_default_mapping()

        # Check structure
        assert isinstance(mapping, dict)
        assert len(mapping) > 0


class TestChatGPTAgent:
    """Tests for ChatGPTAgent."""

    def test_init(self):
        """Test agent initialization."""
        agent = ChatGPTAgent(profile_dir="dummy")
        assert agent is not None


class TestClaudeAgent:
    """Tests for ClaudeAgent."""

    def test_init(self):
        """Test agent initialization."""
        agent = ClaudeAgent(profile_dir="dummy")
        assert agent is not None

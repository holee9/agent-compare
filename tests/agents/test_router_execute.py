"""Focused tests for AgentRouter.execute behavior."""

from types import SimpleNamespace

import pytest

from agents.base import AgentRequest, AgentResponse, AsyncAgent
from agents.router import AgentRouter, PhaseTask
from core.exceptions import AgentException as CoreAgentException
from core.models import AgentType, DocumentType
from src.core.exceptions import AgentException as SrcAgentException


class _DummyGateway:
    pass


class _DummyAgent(AsyncAgent):
    def __init__(self) -> None:
        super().__init__(gateway_provider=_DummyGateway())
        self.last_request: AgentRequest | None = None

    async def execute(self, request: AgentRequest) -> AgentResponse:
        self.last_request = request
        return AgentResponse(
            agent_name="chatgpt",
            task_name=request.task_name,
            content="ok",
            success=True,
        )


@pytest.mark.anyio
async def test_execute_uses_default_timeout_when_settings_missing():
    router = AgentRouter(settings=None)
    agent = _DummyAgent()
    router.register_agent(AgentType.CHATGPT, agent)

    response = await router.execute(
        phase=1,
        task=PhaseTask.BRAINSTORM_CHATGPT,
        prompt="hello",
        doc_type=DocumentType.BIZPLAN,
    )

    assert response.success is True
    assert agent.last_request is not None
    assert agent.last_request.timeout == 120


@pytest.mark.anyio
async def test_execute_uses_settings_timeout():
    router = AgentRouter(settings=SimpleNamespace(timeout_seconds=77))
    agent = _DummyAgent()
    router.register_agent(AgentType.CHATGPT, agent)

    await router.execute(
        phase=1,
        task=PhaseTask.BRAINSTORM_CHATGPT,
        prompt="hello",
        doc_type=DocumentType.BIZPLAN,
    )

    assert agent.last_request is not None
    assert agent.last_request.timeout == 77


@pytest.mark.anyio
async def test_execute_raises_when_mapping_missing():
    router = AgentRouter(settings=None)
    router.register_agent(AgentType.CHATGPT, _DummyAgent())

    with pytest.raises((CoreAgentException, SrcAgentException)):
        await router.execute(
            phase=99,
            task=PhaseTask.BRAINSTORM_CHATGPT,
            prompt="hello",
            doc_type=DocumentType.BIZPLAN,
        )

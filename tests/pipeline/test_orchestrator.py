"""
Tests for orchestrator layer.
"""

from pathlib import Path

import pytest

from agents.base import AgentRequest, AgentResponse, AsyncAgent
from core.models import AgentType, PhaseStatus, PipelineConfig
from pipeline.orchestrator import PipelineOrchestrator
from pipeline.state import PipelineState


class _DummyGateway:
    pass


class _SuccessAgent(AsyncAgent):
    def __init__(self, name: str) -> None:
        super().__init__(gateway_provider=_DummyGateway())
        self._name = name

    async def execute(self, request: AgentRequest) -> AgentResponse:
        return AgentResponse(
            agent_name=self._name,
            task_name=request.task_name,
            content="ok",
            success=True,
        )


class _FailingAgent(AsyncAgent):
    def __init__(self, error: str) -> None:
        super().__init__(gateway_provider=_DummyGateway())
        self._error = error

    async def execute(self, request: AgentRequest) -> AgentResponse:
        raise RuntimeError(self._error)


class TestPipelineState:
    """Tests for PipelineState enum."""

    def test_state_values(self):
        """Test that state values are correct."""
        assert PipelineState.IDLE == "idle"
        assert PipelineState.PHASE_1 == "phase_1"
        assert PipelineState.COMPLETED == "completed"
        assert PipelineState.FAILED == "failed"


class TestPipelineOrchestrator:
    """Tests for PipelineOrchestrator."""

    def test_init(self):
        """Test orchestrator initialization."""
        orchestrator = PipelineOrchestrator(settings=None)
        assert orchestrator is not None

    def test_create_session(self):
        """Test session creation."""
        orchestrator = PipelineOrchestrator(settings=None)

        config = PipelineConfig(
            topic="Test topic",
            doc_type="bizplan",
            template="startup",
        )
        session = orchestrator.create_session(config=config)

        assert session is not None
        assert session.config.topic == "Test topic"

    def test_state_transitions(self):
        """Test state transitions."""
        orchestrator = PipelineOrchestrator(settings=None)

        config = PipelineConfig(
            topic="Test topic",
            doc_type="bizplan",
            template="startup",
        )
        session = orchestrator.create_session(config=config)

        # Start pipeline
        assert session.state == PipelineState.IDLE
        session.state = PipelineState.PHASE_1

        # Complete
        session.state = PipelineState.COMPLETED
        assert session.state == PipelineState.COMPLETED

    @pytest.mark.anyio
    async def test_execute_phase_completed(self):
        orchestrator = PipelineOrchestrator(settings=None)
        orchestrator.agent_router.register_agent(AgentType.CHATGPT, _SuccessAgent("chatgpt"))
        orchestrator.agent_router.register_agent(AgentType.CLAUDE, _SuccessAgent("claude"))
        orchestrator.agent_router.register_agent(AgentType.GEMINI, _SuccessAgent("gemini"))
        orchestrator.agent_router.register_agent(AgentType.PERPLEXITY, _SuccessAgent("perplexity"))

        config = PipelineConfig(topic="Test topic for successful phase")
        session = orchestrator.create_session(config=config)

        result = await orchestrator.execute_phase(session, 1)

        assert result.status == PhaseStatus.COMPLETED
        assert len(result.ai_responses) == 2

    @pytest.mark.anyio
    async def test_execute_phase_failure_adds_single_error_response(self):
        orchestrator = PipelineOrchestrator(settings=None)
        orchestrator.agent_router.register_agent(AgentType.CHATGPT, _SuccessAgent("chatgpt"))
        orchestrator.agent_router.register_agent(AgentType.CLAUDE, _FailingAgent("boom"))

        config = PipelineConfig(topic="Test topic for failed phase")
        session = orchestrator.create_session(config=config)

        result = await orchestrator.execute_phase(session, 1)

        assert result.status == PhaseStatus.FAILED
        assert len(result.ai_responses) == 2
        assert sum(1 for response in result.ai_responses if not response.success) == 1

    @pytest.mark.anyio
    async def test_execute_phase_skipped_when_phase_not_configured(self):
        orchestrator = PipelineOrchestrator(settings=None)
        config = PipelineConfig(topic="Test topic for skipped phase")
        session = orchestrator.create_session(config=config)

        result = await orchestrator.execute_phase(session, 99)

        assert result.status == PhaseStatus.SKIPPED
        assert len(result.ai_responses) == 0

    @pytest.mark.anyio
    async def test_run_pipeline_writes_smoke_outputs(self, tmp_path: Path):
        orchestrator = PipelineOrchestrator(settings=None)
        orchestrator.agent_router.register_agent(AgentType.CHATGPT, _SuccessAgent("chatgpt"))
        orchestrator.agent_router.register_agent(AgentType.CLAUDE, _SuccessAgent("claude"))
        orchestrator.agent_router.register_agent(AgentType.GEMINI, _SuccessAgent("gemini"))
        orchestrator.agent_router.register_agent(AgentType.PERPLEXITY, _SuccessAgent("perplexity"))

        config = PipelineConfig(
            topic="Test topic for smoke pipeline",
            output_dir=tmp_path,
        )

        session = await orchestrator.run_pipeline(config)
        output_dir = tmp_path / session.session_id

        assert session.state.value == "completed"
        assert (output_dir / "pipeline_state.json").exists()
        assert (output_dir / "phase1_results.json").exists()
        assert (output_dir / "phase5_results.json").exists()

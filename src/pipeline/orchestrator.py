"""Pipeline orchestration modules."""

from datetime import datetime
from typing import Any

from src.agents.router import AgentRouter, PhaseTask
from src.core.models import (
    AgentResponse,
    AgentType,
    PhaseResult,
    PhaseStatus,
    PipelineConfig,
    PipelineSession,
    PipelineState,
    create_phase_result,
)
from src.gateway.session import SessionManager
from src.output.formatter import FileExporter
from src.templates.manager import TemplateManager

TOTAL_PHASES = 5


class PipelineOrchestrator:
    """
    Orchestrates pipeline execution with state machine and event system.

    Implements state transitions: IDLE -> PHASE_1 -> ... -> COMPLETED/FAILED
    """

    def __init__(
        self,
        settings: Any = None,
        template_manager: TemplateManager | None = None,
        session_manager: SessionManager | None = None,
    ) -> None:
        """Initialize orchestrator with dependencies."""
        self.settings = settings
        self.template_manager = template_manager or TemplateManager()
        self.session_manager = session_manager or SessionManager()
        self.agent_router = AgentRouter(settings)
        self.current_session: PipelineSession | None = None

    def create_session(self, config: PipelineConfig) -> PipelineSession:
        """Create a new pipeline session."""
        return PipelineSession(config=config)

    @staticmethod
    def get_phase_tasks(phase_number: int) -> list[PhaseTask]:
        """Return configured tasks for each phase."""
        phase_tasks: dict[int, list[PhaseTask]] = {
            1: [PhaseTask.BRAINSTORM_CHATGPT, PhaseTask.VALIDATE_CLAUDE],
            2: [PhaseTask.DEEP_SEARCH_GEMINI, PhaseTask.FACT_CHECK_PERPLEXITY],
            3: [PhaseTask.SWOT_CHATGPT, PhaseTask.NARRATIVE_CLAUDE],
            4: [PhaseTask.BUSINESS_PLAN_CLAUDE, PhaseTask.OUTLINE_CHATGPT, PhaseTask.CHARTS_GEMINI],
            5: [PhaseTask.VERIFY_PERPLEXITY, PhaseTask.FINAL_REVIEW_CLAUDE, PhaseTask.POLISH_CLAUDE],
        }
        return phase_tasks.get(phase_number, [])

    def _save_phase_result(self, exporter: FileExporter | None, result: PhaseResult) -> None:
        if exporter is None:
            return
        exporter.save_json(f"phase{result.phase_number}_results", result.model_dump(mode="json"))

    def _save_pipeline_state(self, exporter: FileExporter | None, session: PipelineSession) -> None:
        if exporter is None:
            return
        exporter.save_json("pipeline_state", session.model_dump(mode="json"))

    @staticmethod
    def _build_template_name(phase_number: int, task: PhaseTask) -> str:
        return f"phase_{phase_number}/{task.value}"

    @staticmethod
    def _finalize_session_state(session: PipelineSession) -> None:
        if session.state == PipelineState.FAILED:
            return
        if session.current_phase == TOTAL_PHASES:
            session.state = PipelineState.COMPLETED
        else:
            session.state = PipelineState.FAILED

    async def execute_phase(self, session: PipelineSession, phase_number: int) -> PhaseResult:
        """
        Execute a single pipeline phase.

        Args:
            session: Current pipeline session
            phase_number: Phase to execute (1-5)

        Returns:
            PhaseResult with execution results
        """
        tasks = self.get_phase_tasks(phase_number)
        phase_name = f"Phase {phase_number}"
        result = create_phase_result(phase_number, phase_name)

        if not tasks:
            result.status = PhaseStatus.SKIPPED
            result.completed_at = datetime.now()
            return result

        responses: list[AgentResponse] = []
        failed = False

        for task in tasks:
            prompt = self.template_manager.render_prompt(
                template_name=self._build_template_name(phase_number, task),
                context={
                    "topic": session.config.topic,
                    "doc_type": session.config.doc_type.value,
                    "language": session.config.language,
                },
            )

            try:
                response = await self.agent_router.execute(
                    phase=phase_number,
                    task=task,
                    prompt=prompt,
                    doc_type=session.config.doc_type,
                )
                normalized_response = AgentResponse(
                    agent_name=AgentType(response.agent_name),
                    task_name=response.task_name,
                    content=response.content,
                    tokens_used=response.tokens_used,
                    response_time=response.response_time,
                    success=response.success,
                    error=response.error,
                )
                responses.append(normalized_response)
                if not normalized_response.success:
                    failed = True
            except Exception as exc:  # pragma: no cover - covered through error path assertions
                failed = True
                responses.append(
                    AgentResponse(
                        agent_name=AgentType.CHATGPT,
                        task_name=task.value,
                        content="",
                        success=False,
                        error=str(exc),
                    )
                )

        result.ai_responses = responses
        result.status = PhaseStatus.FAILED if failed else PhaseStatus.COMPLETED
        result.completed_at = datetime.now()
        return result

    async def run_pipeline(self, config: PipelineConfig) -> PipelineSession:
        """
        Run complete pipeline from start to finish.

        Args:
            config: Pipeline configuration

        Returns:
            PipelineSession with all results
        """
        session = self.create_session(config)
        self.current_session = session
        output_dir = config.output_dir / session.session_id
        output_dir.mkdir(parents=True, exist_ok=True)
        exporter = FileExporter(output_dir)

        try:
            for phase_num in range(1, TOTAL_PHASES + 1):
                result = await self.execute_phase(session, phase_num)
                session.add_result(result)
                self._save_phase_result(exporter, result)

                if result.status in {PhaseStatus.COMPLETED, PhaseStatus.SKIPPED}:
                    session.state = PipelineState(f"phase_{phase_num}")
                elif result.status == PhaseStatus.FAILED:
                    session.state = PipelineState.FAILED
                    break

            self._finalize_session_state(session)
        finally:
            self._save_pipeline_state(exporter, session)

        return session

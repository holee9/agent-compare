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
from src.pipeline.base import BasePhase
from src.pipeline.phase1_framing import Phase1Framing
from src.pipeline.phase2_research import Phase2Research
from src.pipeline.phase3_strategy import Phase3Strategy
from src.pipeline.phase4_writing import Phase4Writing
from src.pipeline.phase5_review import Phase5Review
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
        enable_ui: bool = False,
    ) -> None:
        """
        Initialize orchestrator with dependencies.

        Args:
            settings: Configuration settings
            template_manager: Template manager for prompt rendering
            session_manager: Session manager for browser sessions
            enable_ui: Enable Rich UI components (progress, logging, summary)
        """
        self.settings = settings
        self.template_manager = template_manager or TemplateManager()
        self.session_manager = session_manager or SessionManager()
        self.agent_router = AgentRouter(settings)
        self.current_session: PipelineSession | None = None
        self.enable_ui = enable_ui

        # Initialize phase classes
        self._phases: dict[int, BasePhase] = {
            1: Phase1Framing(self.template_manager, self.agent_router),
            2: Phase2Research(self.template_manager, self.agent_router),
            3: Phase3Strategy(self.template_manager, self.agent_router),
            4: Phase4Writing(self.template_manager, self.agent_router),
            5: Phase5Review(self.template_manager, self.agent_router),
        }

        # Initialize UI components if enabled
        if self.enable_ui:
            from rich.console import Console

            from src.ui.logger import LogStream
            from src.ui.progress import PipelineProgress
            from src.ui.summary import PhaseSummary

            console = Console()
            self.ui_progress = PipelineProgress(console)
            self.ui_logger = LogStream(console)
            self.ui_summary = PhaseSummary(console)
        else:
            self.ui_progress = None
            self.ui_logger = None
            self.ui_summary = None

    def create_session(self, config: PipelineConfig) -> PipelineSession:
        """Create a new pipeline session."""
        return PipelineSession(config=config)

    def get_phase_tasks(self, phase_number: int) -> list[PhaseTask]:
        """
        Return configured tasks for each phase.

        This method is kept for backward compatibility.
        It delegates to the phase classes.

        Args:
            phase_number: Phase number (1-5)

        Returns:
            List of PhaseTask enum values
        """
        phase = self._phases.get(phase_number)
        if phase is None:
            return []

        # Create a dummy session to call get_tasks
        config = PipelineConfig(topic="Dummy topic for getting phase tasks")
        session = PipelineSession(config=config)
        return phase.get_tasks(session)

    def _save_phase_result(self, exporter: FileExporter | None, result: PhaseResult) -> None:
        if exporter is None:
            return
        exporter.save_json(f"phase{result.phase_number}_results", result.model_dump(mode="json"))

    def _save_pipeline_state(self, exporter: FileExporter | None, session: PipelineSession) -> None:
        if exporter is None:
            return
        exporter.save_json("pipeline_state", session.model_dump(mode="json"))

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
        # Get the appropriate phase class
        phase = self._phases.get(phase_number)

        if phase is None:
            # Phase not configured, return skipped result
            result = create_phase_result(phase_number, f"Phase {phase_number}")
            result.status = PhaseStatus.SKIPPED
            result.completed_at = datetime.now()
            return result

        # Log phase start if UI enabled
        if self.ui_logger:
            self.ui_logger.info(f"Starting Phase {phase_number}: {phase.get_phase_number()}")

        # Execute the phase
        result = await phase.execute(session, session.config)

        # Update UI progress if enabled
        if self.ui_progress and phase_number <= 5:
            phase_names = {
                1: "Framing",
                2: "Research",
                3: "Strategy",
                4: "Writing",
                5: "Review",
            }
            # Get first agent from responses for display
            agent_name = "Unknown"
            if result.ai_responses:
                agent_name = result.ai_responses[0].agent_name.value

            self.ui_progress.update_phase(
                phase_number=phase_number,
                phase_name=phase_names.get(phase_number, f"Phase {phase_number}"),
                agent_name=agent_name,
            )

        # Log phase completion if UI enabled
        if self.ui_logger:
            if result.status == PhaseStatus.COMPLETED:
                self.ui_logger.info(f"Phase {phase_number} completed successfully")
            elif result.status == PhaseStatus.FAILED:
                self.ui_logger.error(f"Phase {phase_number} failed")
            else:
                self.ui_logger.warning(f"Phase {phase_number} skipped")

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

        # Start UI progress if enabled
        if self.ui_progress:
            self.ui_progress.start(total_phases=TOTAL_PHASES)

        # Log pipeline start if UI enabled
        if self.ui_logger:
            self.ui_logger.info(f"Starting pipeline for topic: {config.topic}")

        try:
            for phase_num in range(1, TOTAL_PHASES + 1):
                result = await self.execute_phase(session, phase_num)
                session.add_result(result)
                self._save_phase_result(exporter, result)

                if result.status in {PhaseStatus.COMPLETED, PhaseStatus.SKIPPED}:
                    session.state = PipelineState(f"phase_{phase_num}")
                elif result.status == PhaseStatus.FAILED:
                    session.state = PipelineState.FAILED
                    if self.ui_logger:
                        self.ui_logger.error("Pipeline failed, stopping execution")
                    break

            self._finalize_session_state(session)

            # Stop UI progress and show summary if enabled
            if self.ui_progress:
                self.ui_progress.stop()
                self.ui_progress.show_session_summary(session)

            if self.ui_summary:
                self.ui_summary.show_session_phases(session)

            # Log pipeline completion if UI enabled
            if self.ui_logger:
                if session.state == PipelineState.COMPLETED:
                    self.ui_logger.info("Pipeline completed successfully!")
                else:
                    self.ui_logger.warning(f"Pipeline ended with state: {session.state.value}")

        finally:
            self._save_pipeline_state(exporter, session)

        return session

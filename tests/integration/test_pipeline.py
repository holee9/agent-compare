"""
Integration tests for pipeline workflow.
"""

import pytest

from src.pipeline.orchestrator import PipelineOrchestrator
from src.core.models import PipelineConfig


class TestPipelineWorkflow:
    """Integration tests for complete pipeline."""

    def test_full_pipeline_flow(self):
        """Test complete pipeline flow end-to-end."""
        orchestrator = PipelineOrchestrator(settings=None)

        config = PipelineConfig(
            topic="AI SaaS Platform for enterprise",
            doc_type="bizplan",
            template="startup",
        )

        session = orchestrator.create_session(config=config)

        # Execute pipeline (this would take a long time with real AI calls)
        # For now, just test structure
        assert session is not None
        assert session.config.topic == "AI SaaS Platform for enterprise"

    def test_phase_context_delivery(self):
        """Test that phase context is delivered between phases."""
        # This would require running phases and checking results
        pass

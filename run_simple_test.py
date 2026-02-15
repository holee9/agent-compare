"""
Simple pipeline test runner for validation.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.pipeline.orchestrator import PipelineOrchestrator
from src.core.models import PipelineConfig


async def main():
    """Run simple pipeline test."""
    print("=" * 60)
    print("AigenFlow Simple Pipeline Test")
    print("=" * 60)

    # Test 1: Business Plan (ChatGPT only)
    print("\n[Test 1] Startup Business Plan")
    print("-" * 40)

    orchestrator = PipelineOrchestrator(settings=None)

    config = PipelineConfig(
        topic="AI 스타트업 비즈니스 플랜: 자동화 고객 관리 시스템",
        doc_type="bizplan",
        template="startup",
        language="ko",
    )

    try:
        session = orchestrator.create_session(config=config)
        print(f"✅ Session created: {session.session_id}")
        # session.config is PipelineConfig object
        print(f"   Topic: {session.config.topic}")
        print(f"   State: {session.state}")

        # Try to run first phase
        print("\n[Phase 1] Attempting execution...")
        result = await orchestrator.execute_phase(session, 1)
        print(f"✅ Phase 1 completed")
        print(f"   Status: {result.status}")
        print(f"   AI Responses: {len(result.ai_responses)}")
        for i, resp in enumerate(result.ai_responses):
            print(f"   [{i+1}] {resp.agent_name}: {len(resp.content)} chars")

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

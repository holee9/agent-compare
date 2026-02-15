"""
Real pipeline test with registered agents.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.pipeline.orchestrator import PipelineOrchestrator
from src.core.models import PipelineConfig
from src.core.config import get_settings
from src.agents.chatgpt_agent import ChatGPTAgent
from src.agents.claude_agent import ClaudeAgent
from src.agents.gemini_agent import GeminiAgent
from src.agents.perplexity_agent import PerplexityAgent


async def main():
    """Run real pipeline test with agents."""
    print("=" * 60)
    print("AigenFlow Real Pipeline Test")
    print("=" * 60)

    # Get settings
    settings = get_settings()
    print(f"\nSettings:")
    print(f"  Profiles Dir: {settings.profiles_dir}")
    print(f"  Output Dir: {settings.output_dir}")
    print(f"  Timeout: {settings.timeout_seconds}s")

    # Create orchestrator
    orchestrator = PipelineOrchestrator(settings=settings)

    # Register agents
    print(f"\n[Setup] Registering agents...")
    profiles_dir = settings.profiles_dir

    try:
        chatgpt = ChatGPTAgent(profile_dir=profiles_dir / "chatgpt", headless=settings.gateway_headless)
        orchestrator.agent_router.register_agent("chatgpt", chatgpt)
        print(f"  ✅ ChatGPT registered")
    except Exception as e:
        print(f"  ⚠️ ChatGPT: {e}")

    try:
        claude = ClaudeAgent(profile_dir=profiles_dir / "claude", headless=settings.gateway_headless)
        orchestrator.agent_router.register_agent("claude", claude)
        print(f"  ✅ Claude registered")
    except Exception as e:
        print(f"  ⚠️ Claude: {e}")

    try:
        gemini = GeminiAgent(profile_dir=profiles_dir / "gemini", headless=settings.gateway_headless)
        orchestrator.agent_router.register_agent("gemini", gemini)
        print(f"  ✅ Gemini registered")
    except Exception as e:
        print(f"  ⚠️ Gemini: {e}")

    try:
        perplexity = PerplexityAgent(profile_dir=profiles_dir / "perplexity", headless=settings.gateway_headless)
        orchestrator.agent_router.register_agent("perplexity", perplexity)
        print(f"  ✅ Perplexity registered")
    except Exception as e:
        print(f"  ⚠️ Perplexity: {e}")

    # Test configuration
    print(f"\n[Test 1] Startup Business Plan")
    print("-" * 40)

    config = PipelineConfig(
        topic="AI 스타트업 비즈니스 플랜: 자동화 고객 관리 시스템",
        doc_type="bizplan",
        template="startup",
        language="ko",
    )

    try:
        session = orchestrator.create_session(config=config)
        print(f"✅ Session created: {session.session_id}")
        print(f"   Topic: {session.config.topic}")
        print(f"   State: {session.state}")

        # Try to run first phase
        print(f"\n[Phase 1] Attempting execution...")
        result = await orchestrator.execute_phase(session, 1)
        print(f"✅ Phase 1 completed")
        print(f"   Status: {result.status}")
        print(f"   AI Responses: {len(result.ai_responses)}")

        for i, resp in enumerate(result.ai_responses):
            status_icon = "✅" if resp.success else "❌"
            print(f"   {status_icon} [{i+1}] {resp.agent_name}:")
            print(f"      Task: {resp.task_name}")
            print(f"      Content: {len(resp.content)} chars")
            if resp.error:
                print(f"      Error: {resp.error}")

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

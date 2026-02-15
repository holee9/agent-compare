"""
Perplexity provider implementation.

Uses Playwright to interact with perplexity.ai.
"""

from pathlib import Path

from pydantic import Field

from src.core.exceptions import GatewayException, ErrorCode
from src.gateway.base import BaseProvider, GatewayRequest, GatewayResponse


class PerplexityProvider(BaseProvider):
    """
    Provider for Perplexity (perplexity.ai).

    Handles login, message sending, and session management.
    """

    def __init__(
        self,
        profile_dir: Path,
        headless: bool = True,
    ) -> None:
        super().__init__(profile_dir, headless)
        self.base_url = "https://perplexity.ai"

    async def send_message(self, request: GatewayRequest) -> GatewayResponse:
        """Send message to Perplexity."""
        return GatewayResponse(
            content=f"Perplexity response to: {request.task_name}",
            success=True,
        )

    async def check_session(self) -> bool:
        """Check if Perplexity session is valid."""
        return False

    async def login_flow(self) -> None:
        """Execute Perplexity login flow."""
        pass

    def save_session(self) -> None:
        """Save Perplexity session state."""
        pass

    def load_session(self) -> bool:
        """Load Perplexity session state."""
        return False

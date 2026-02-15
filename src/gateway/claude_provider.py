"""
Claude provider implementation.

Uses Playwright to interact with claude.ai.
"""

from pathlib import Path

from pydantic import Field

from src.core.exceptions import GatewayException, ErrorCode
from src.gateway.base import BaseProvider, GatewayRequest, GatewayResponse


class ClaudeProvider(BaseProvider):
    """
    Provider for Claude (claude.ai).

    Handles login, message sending, and session management.
    """

    def __init__(
        self,
        profile_dir: Path,
        headless: bool = True,
    ) -> None:
        super().__init__(profile_dir, headless)
        self.base_url = "https://claude.ai"

    async def send_message(self, request: GatewayRequest) -> GatewayResponse:
        """Send message to Claude."""
        # TODO: Implement Playwright interaction
        return GatewayResponse(
            content=f"Claude response to: {request.task_name}",
            success=True,
        )

    async def check_session(self) -> bool:
        """Check if Claude session is valid."""
        return False

    async def login_flow(self) -> None:
        """Execute Claude login flow."""
        pass

    def save_session(self) -> None:
        """Save Claude session state."""
        pass

    def load_session(self) -> bool:
        """Load Claude session state."""
        return False

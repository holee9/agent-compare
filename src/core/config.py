"""
Configuration management for agent-compare pipeline.
"""

from pathlib import Path
from typing import Literal

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentCompareSettings(BaseSettings):
    """Application settings for agent-compare."""

    model_config = ConfigDict(extra="ignore")

    app_name: str = "agent-compare"
    debug: bool = False
    log_level: str = "INFO"
    log_format: Literal["json", "pretty"] = "pretty"

    output_dir: Path = Field(default_factory=lambda: Path("output"))
    profiles_dir: Path = Field(default_factory=lambda: Path("~/.agent-compare/profiles").expanduser())
    templates_dir: Path = Field(default_factory=lambda: Path("templates"))

    max_retries: int = 2
    timeout_seconds: int = 120
    enable_auto_save: bool = True

    gateway_timeout: int = 120
    gateway_headless: bool = True
    gateway_user_data_dir: Path | None = None

    enable_parallel_phases: bool = True
    enable_event_tracking: bool = True

    # API Keys (ignored in settings if not provided)
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    perplexity_session_token: str | None = None
    perplexity_csrf_token: str | None = None

    @field_validator("output_dir", "profiles_dir", "templates_dir")
    def create_directories(cls, v: Path) -> Path:
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("log_level")
    def normalize_log_level(cls, v: str) -> str:
        return v.upper()

    model_config = ConfigDict(
        extra="ignore",
        env_prefix="AC",
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
    )


def get_settings() -> AgentCompareSettings:
    """Get application settings instance."""
    return AgentCompareSettings()


def get_output_dir(session_id: str, settings: AgentCompareSettings | None = None) -> Path:
    """Get output directory for a specific session."""
    if settings is None:
        settings = get_settings()

    output_path = settings.output_dir / session_id
    output_path.mkdir(parents=True, exist_ok=True)

    for i in range(1, 6):
        phase_dir = output_path / f"phase{i}"
        phase_dir.mkdir(exist_ok=True)

    final_dir = output_path / "final"
    final_dir.mkdir(exist_ok=True)

    return output_path

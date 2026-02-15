"""
Test configuration for all modules.
"""

import pytest
from pathlib import Path

from src.core.config import AgentCompareSettings
from src.gateway.base import BaseProvider


def test_settings_loading():
    """Test that settings can be loaded."""
    settings = AgentCompareSettings()

    assert settings.app_name == "agent-compare"
    assert settings.output_dir == Path("output")
    assert settings.profiles_dir == Path("~/.agent-compare/profiles").expanduser()


def test_profile_directory_creation():
    """Test that profile directory is created if needed."""
    settings = AgentCompareSettings()
    profiles_dir = settings.profiles_dir

    # Directory should be created by settings validation
    assert profiles_dir.exists()

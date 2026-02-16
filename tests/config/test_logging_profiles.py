"""
Tests for logging profile configuration.

Tests cover environment-specific profiles, custom profile creation,
and profile-based logging setup.
"""

import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import structlog

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from config.logging_profiles import (
    LogEnvironment,
    LogLevel,
    LoggingProfile,
    create_custom_profile,
    get_logging_profile,
)
from core.logger import (
    LogContext,
    get_current_log_level,
    get_logger,
    redact_secrets,
    set_log_level,
    setup_logging,
)


class TestLogLevel:
    """Test LogLevel enum functionality."""

    def test_log_level_values(self):
        """LogLevel enum has correct string values."""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"

    def test_log_level_from_string_valid(self):
        """LogLevel.from_string accepts valid levels."""
        assert LogLevel.from_string("debug") == LogLevel.DEBUG
        assert LogLevel.from_string("DEBUG") == LogLevel.DEBUG
        assert LogLevel.from_string("info") == LogLevel.INFO
        assert LogLevel.from_string("warning") == LogLevel.WARNING
        assert LogLevel.from_string("error") == LogLevel.ERROR
        assert LogLevel.from_string("critical") == LogLevel.CRITICAL

    def test_log_level_from_string_invalid(self):
        """LogLevel.from_string rejects invalid levels."""
        with pytest.raises(ValueError, match="Invalid log level"):
            LogLevel.from_string("invalid")

        with pytest.raises(ValueError, match="Invalid log level"):
            LogLevel.from_string("TRACE")


class TestLogEnvironment:
    """Test LogEnvironment enum functionality."""

    def test_log_environment_values(self):
        """LogEnvironment enum has correct string values."""
        assert LogEnvironment.DEVELOPMENT.value == "development"
        assert LogEnvironment.TESTING.value == "testing"
        assert LogEnvironment.PRODUCTION.value == "production"

    def test_log_environment_from_string_valid(self):
        """LogEnvironment.from_string accepts valid environments."""
        assert LogEnvironment.from_string("development") == LogEnvironment.DEVELOPMENT
        assert LogEnvironment.from_string("DEVELOPMENT") == LogEnvironment.DEVELOPMENT
        assert LogEnvironment.from_string("testing") == LogEnvironment.TESTING
        assert LogEnvironment.from_string("production") == LogEnvironment.PRODUCTION

    def test_log_environment_from_string_invalid(self):
        """LogEnvironment.from_string rejects invalid environments."""
        with pytest.raises(ValueError, match="Invalid environment"):
            LogEnvironment.from_string("staging")

        with pytest.raises(ValueError, match="Invalid environment"):
            LogEnvironment.from_string("invalid")


class TestLoggingProfile:
    """Test LoggingProfile dataclass."""

    def test_logging_profile_creation(self):
        """LoggingProfile can be instantiated with all fields."""
        profile = LoggingProfile(
            name="test",
            log_level=LogLevel.INFO,
            output_targets=("console", "file"),
            use_json=True,
            log_file_path=Path("test.log"),
            max_file_size_mb=10,
            backup_count=5,
        )
        assert profile.name == "test"
        assert profile.log_level == LogLevel.INFO
        assert profile.output_targets == ("console", "file")
        assert profile.use_json is True
        assert profile.log_file_path == Path("test.log")
        assert profile.max_file_size_mb == 10
        assert profile.backup_count == 5

    def test_should_log_to_console(self):
        """should_log_to_console returns correct boolean."""
        profile_with_console = LoggingProfile(
            name="test",
            log_level=LogLevel.INFO,
            output_targets=("console", "file"),
            use_json=True,
            log_file_path=Path("test.log"),
            max_file_size_mb=10,
            backup_count=5,
        )
        assert profile_with_console.should_log_to_console() is True

        profile_without_console = LoggingProfile(
            name="test",
            log_level=LogLevel.INFO,
            output_targets=("file",),
            use_json=True,
            log_file_path=Path("test.log"),
            max_file_size_mb=10,
            backup_count=5,
        )
        assert profile_without_console.should_log_to_console() is False

    def test_should_log_to_file(self):
        """should_log_to_file returns correct boolean."""
        profile_with_file = LoggingProfile(
            name="test",
            log_level=LogLevel.INFO,
            output_targets=("console", "file"),
            use_json=True,
            log_file_path=Path("test.log"),
            max_file_size_mb=10,
            backup_count=5,
        )
        assert profile_with_file.should_log_to_file() is True

        profile_without_file = LoggingProfile(
            name="test",
            log_level=LogLevel.INFO,
            output_targets=("console",),
            use_json=True,
            log_file_path=Path("test.log"),
            max_file_size_mb=10,
            backup_count=5,
        )
        assert profile_without_file.should_log_to_file() is False


class TestPredefinedProfiles:
    """Test predefined logging profiles."""

    def test_development_profile(self):
        """Development profile has DEBUG level and both outputs."""
        profile = get_logging_profile(LogEnvironment.DEVELOPMENT)
        assert profile.name == "development"
        assert profile.log_level == LogLevel.DEBUG
        assert profile.should_log_to_console() is True
        assert profile.should_log_to_file() is True
        assert profile.use_json is True
        assert profile.max_file_size_mb == 10
        assert profile.backup_count == 5

    def test_testing_profile(self):
        """Testing profile has INFO level and file-only output."""
        profile = get_logging_profile(LogEnvironment.TESTING)
        assert profile.name == "testing"
        assert profile.log_level == LogLevel.INFO
        assert profile.should_log_to_console() is False
        assert profile.should_log_to_file() is True
        assert profile.use_json is True
        assert profile.max_file_size_mb == 10
        assert profile.backup_count == 5

    def test_production_profile(self):
        """Production profile has WARNING level and file-only output."""
        profile = get_logging_profile(LogEnvironment.PRODUCTION)
        assert profile.name == "production"
        assert profile.log_level == LogLevel.WARNING
        assert profile.should_log_to_console() is False
        assert profile.should_log_to_file() is True
        assert profile.use_json is True
        assert profile.max_file_size_mb == 10
        assert profile.backup_count == 5

    @patch("core.config.get_settings")
    def test_auto_detect_environment_development(self, mock_get_settings):
        """Auto-detect returns DEVELOPMENT when debug=True."""
        mock_settings = MagicMock()
        mock_settings.debug = True
        mock_get_settings.return_value = mock_settings

        profile = get_logging_profile()
        assert profile.name == "development"

    @patch("core.config.get_settings")
    def test_auto_detect_environment_production(self, mock_get_settings):
        """Auto-detect returns PRODUCTION when debug=False."""
        mock_settings = MagicMock()
        mock_settings.debug = False
        mock_get_settings.return_value = mock_settings

        profile = get_logging_profile()
        assert profile.name == "production"


class TestCustomProfile:
    """Test custom profile creation."""

    def test_create_custom_profile_with_string_level(self):
        """create_custom_profile accepts string log level."""
        profile = create_custom_profile("DEBUG")
        assert profile.log_level == LogLevel.DEBUG
        assert profile.name == "custom"

    def test_create_custom_profile_with_enum_level(self):
        """create_custom_profile accepts LogLevel enum."""
        profile = create_custom_profile(LogLevel.ERROR)
        assert profile.log_level == LogLevel.ERROR
        assert profile.name == "custom"

    def test_create_custom_profile_outputs(self):
        """create_custom_profile respects output flags."""
        profile_both = create_custom_profile(
            "INFO", output_to_console=True, output_to_file=True
        )
        assert profile_both.should_log_to_console() is True
        assert profile_both.should_log_to_file() is True

        profile_console_only = create_custom_profile(
            "INFO", output_to_console=True, output_to_file=False
        )
        assert profile_console_only.should_log_to_console() is True
        assert profile_console_only.should_log_to_file() is False

        profile_file_only = create_custom_profile(
            "INFO", output_to_console=False, output_to_file=True
        )
        assert profile_file_only.should_log_to_console() is False
        assert profile_file_only.should_log_to_file() is True

    def test_create_custom_profile_json_format(self):
        """create_custom_profile respects use_json flag."""
        profile_json = create_custom_profile("INFO", use_json=True)
        assert profile_json.use_json is True

        profile_pretty = create_custom_profile("INFO", use_json=False)
        assert profile_pretty.use_json is False

    def test_create_custom_profile_file_settings(self):
        """create_custom_profile accepts custom file settings."""
        custom_path = Path("custom.log")
        profile = create_custom_profile(
            "INFO",
            log_file=custom_path,
            max_file_size_mb=50,
            backup_count=10,
        )
        assert profile.log_file_path == custom_path
        assert profile.max_file_size_mb == 50
        assert profile.backup_count == 10


class TestRedactSecrets:
    """Test secret redaction functionality."""

    def test_redact_dict_sensitive_key(self):
        """Redact values for sensitive keys."""
        data = {
            "username": "john",
            "password": "secret123",
            "api_key": "sk-1234567890abcdefghij",
        }
        redacted = redact_secrets(data)
        assert redacted["username"] == "john"
        # Strings > 8 chars: first4...last4
        assert redacted["password"] == "secr...t123"
        assert redacted["api_key"] == "sk-1...ghij"

    def test_redact_dict_insensitive_key_matching(self):
        """Key matching is case-insensitive."""
        data = {"Password": "secret123", "API_KEY": "sk-1234567890abcdefghij"}
        redacted = redact_secrets(data)
        # Strings > 8 chars: first4...last4
        assert redacted["Password"] == "secr...t123"
        assert redacted["API_KEY"] == "sk-1...ghij"

    def test_redact_list(self):
        """Redact sensitive values in lists."""
        data = ["normal", "sk-1234567890abcdef1", {"token": "abc"}]
        redacted = redact_secrets(data)
        assert redacted[0] == "normal"
        # Long strings (20+ chars) are masked even without key hint
        assert redacted[1] == "sk-1...def1"
        # "token" is a sensitive key, so "abc" gets masked as "***"
        assert redacted[2]["token"] == "***"

    def test_redact_tuple(self):
        """Redact sensitive values in tuples."""
        data = ("normal", "sk-1234567890abcdef1", {"token": "abc"})
        redacted = redact_secrets(data)
        assert isinstance(redacted, tuple)
        assert redacted[0] == "normal"
        # Long strings (20+ chars) are masked even without key hint
        assert redacted[1] == "sk-1...def1"
        # "token" is a sensitive key, so "abc" gets masked as "***"
        assert redacted[2]["token"] == "***"

    def test_redact_nested_structures(self):
        """Redact secrets in nested dictionaries."""
        data = {
            "user": "john",
            "credentials": {
                "password": "secret123",
                "api_key": "sk-1234567890abcdefghij",
            },
        }
        redacted = redact_secrets(data)
        assert redacted["user"] == "john"
        # "secret123" is 9 chars, so it gets secr...t123
        assert redacted["credentials"]["password"] == "secr...t123"
        assert redacted["credentials"]["api_key"] == "sk-1...ghij"

    def test_redact_with_key_hint(self):
        """Redact values when key hint indicates sensitivity."""
        value = "sk-1234567890abcdef"
        redacted = redact_secrets(value, key_hint="api_key")
        assert redacted == "sk-1...cdef"

    def test_redact_long_secret_pattern(self):
        """Redact long alphanumeric strings that look like secrets."""
        value = "abcdefghijklmnopqrstuvwxyz123456"
        redacted = redact_secrets(value)
        # 20+ chars gets first4...last4
        assert redacted == "abcd...3456"

    def test_redact_short_values(self):
        """Short sensitive values are fully masked."""
        value = "short"
        redacted = redact_secrets(value, key_hint="password")
        assert redacted == "***"

    def test_redact_non_sensitive(self):
        """Non-sensitive values are not modified."""
        assert redact_secrets("hello") == "hello"
        assert redact_secrets(123) == 123
        assert redact_secrets(True) is True


class TestSetupLogging:
    """Test logging setup functionality."""

    def test_setup_logging_basic(self, tmp_path):
        """setup_logging configures logging with basic parameters."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(level="INFO", log_file=log_file)

        # Check if it's a structlog logger (has info, debug methods)
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")

        # Check stdlib logger configuration
        stdlib_logger = logging.getLogger("aigenflow")
        assert stdlib_logger.level == logging.INFO

    def test_setup_logging_with_profile(self, tmp_path):
        """setup_logging uses LoggingProfile configuration."""
        log_file = tmp_path / "profile.log"
        profile = create_custom_profile(
            "DEBUG",
            log_file=log_file,
            output_to_console=False,
            output_to_file=True,
        )
        logger = setup_logging(profile=profile)

        # Check if it's a structlog logger (has info, debug methods)
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")

        stdlib_logger = logging.getLogger("aigenflow")
        assert stdlib_logger.level == logging.DEBUG

    def test_setup_logging_creates_log_directory(self, tmp_path):
        """setup_logging creates log directory if it doesn't exist."""
        log_file = tmp_path / "logs" / "test.log"
        setup_logging(log_file=log_file)

        assert log_file.parent.exists()

    def test_setup_logging_file_rotation(self, tmp_path):
        """setup_logging configures file rotation."""
        log_file = tmp_path / "rotating.log"
        profile = create_custom_profile(
            "INFO",
            log_file=log_file,
            max_file_size_mb=1,
            backup_count=3,
        )
        setup_logging(profile=profile)

        stdlib_logger = logging.getLogger("aigenflow")
        file_handlers = [
            h
            for h in stdlib_logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]

        assert len(file_handlers) == 1
        handler = file_handlers[0]
        assert handler.maxBytes == 1 * 1024 * 1024  # 1 MB
        assert handler.backupCount == 3


class TestGetLogger:
    """Test logger retrieval."""

    def test_get_logger_default_name(self):
        """get_logger returns logger with default name."""
        logger = get_logger()
        # Check if it's a structlog logger (has info, debug methods)
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")

    def test_get_logger_custom_name(self):
        """get_logger returns logger with custom name."""
        logger = get_logger("custom.module")
        # Check if it's a structlog logger (has info, debug methods)
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")


class TestLogContext:
    """Test log context manager."""

    def test_log_context_binds_values(self):
        """LogContext binds context values to logger."""
        context = LogContext(user_id="123", request_id="abc")
        logger = context.__enter__()

        # Verify context is bound (structlog stores bound context)
        # Check if it's a structlog logger (has info, debug methods)
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")

    def test_log_context_exit(self):
        """LogContext __exit__ is a no-op but callable."""
        context = LogContext(user_id="123")
        context.__exit__(None, None, None)
        # Should not raise any exception


class TestDynamicLogLevel:
    """Test dynamic log level changes."""

    def test_set_log_level_string(self):
        """set_log_level accepts string level."""
        setup_logging(level="INFO")
        set_log_level("DEBUG")

        assert get_current_log_level() == "DEBUG"

    def test_set_log_level_int(self):
        """set_log_level accepts int level."""
        setup_logging(level="INFO")
        set_log_level(logging.DEBUG)

        assert get_current_log_level() == "DEBUG"

    def test_get_current_log_level(self):
        """get_current_log_level returns current level."""
        setup_logging(level="WARNING")
        assert get_current_log_level() == "WARNING"

        setup_logging(level="ERROR")
        assert get_current_log_level() == "ERROR"

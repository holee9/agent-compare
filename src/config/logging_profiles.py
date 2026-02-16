"""
Logging profile configuration for AigenFlow pipeline.

Provides environment-specific logging profiles with different log levels,
output targets, and formatting options.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class LogLevel(Enum):
    """Standard logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "LogLevel":
        """Create LogLevel from string, case-insensitive."""
        try:
            return cls[value.upper()]
        except KeyError:
            valid = ", ".join(level.name for level in cls)
            raise ValueError(
                f"Invalid log level: {value!r}. Valid levels: {valid}"
            ) from None


class LogEnvironment(Enum):
    """Logging environment presets."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "LogEnvironment":
        """Create LogEnvironment from string, case-insensitive."""
        try:
            return cls[value.upper()]
        except KeyError:
            valid = ", ".join(env.name for env in cls)
            raise ValueError(
                f"Invalid environment: {value!r}. Valid environments: {valid}"
            ) from None


@dataclass(frozen=True)
class LoggingProfile:
    """
    Logging configuration profile.

    Attributes:
        name: Profile name for identification
        log_level: Minimum log level to record
        output_targets: List of output destinations ("console", "file")
        use_json: Whether to use JSON format (vs pretty console format)
        log_file_path: Path for file logging (when "file" in output_targets)
        max_file_size_mb: Maximum file size before rotation (MB)
        backup_count: Number of backup files to keep
    """

    name: str
    log_level: LogLevel
    output_targets: tuple[str, ...]
    use_json: bool
    log_file_path: Path
    max_file_size_mb: int
    backup_count: int

    def should_log_to_console(self) -> bool:
        """Check if console logging is enabled."""
        return "console" in self.output_targets

    def should_log_to_file(self) -> bool:
        """Check if file logging is enabled."""
        return "file" in self.output_targets


def _get_default_log_file() -> Path:
    """Get default log file path from settings."""
    from core.config import get_settings

    settings = get_settings()
    log_dir = settings.output_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "aigenflow.log"


def _create_profile_for_environment(environment: LogEnvironment) -> LoggingProfile:
    """Create a logging profile for the specified environment."""
    log_file = _get_default_log_file()

    if environment == LogEnvironment.DEVELOPMENT:
        return LoggingProfile(
            name="development",
            log_level=LogLevel.DEBUG,
            output_targets=("console", "file"),
            use_json=True,
            log_file_path=log_file,
            max_file_size_mb=10,
            backup_count=5,
        )
    elif environment == LogEnvironment.TESTING:
        return LoggingProfile(
            name="testing",
            log_level=LogLevel.INFO,
            output_targets=("file",),
            use_json=True,
            log_file_path=log_file,
            max_file_size_mb=10,
            backup_count=5,
        )
    else:  # PRODUCTION
        return LoggingProfile(
            name="production",
            log_level=LogLevel.WARNING,
            output_targets=("file",),
            use_json=True,
            log_file_path=log_file,
            max_file_size_mb=10,
            backup_count=5,
        )


def get_logging_profile(
    environment: LogEnvironment | None = None,
) -> LoggingProfile:
    """
    Get logging profile for the specified environment.

    Args:
        environment: Environment to get profile for. If None, detects
            from AC_DEBUG environment variable or defaults to production.

    Returns:
        LoggingProfile configuration for the environment.

    Examples:
        >>> profile = get_logging_profile(LogEnvironment.DEVELOPMENT)
        >>> profile.log_level
        <LogLevel.DEBUG: 'DEBUG'>

        >>> # Auto-detect from environment
        >>> profile = get_logging_profile()
    """
    if environment is None:
        # Auto-detect from settings
        from core.config import get_settings

        settings = get_settings()
        environment = (
            LogEnvironment.DEVELOPMENT
            if settings.debug
            else LogEnvironment.PRODUCTION
        )

    return _create_profile_for_environment(environment)


def create_custom_profile(
    log_level: str | LogLevel,
    *,
    use_json: bool = True,
    log_file: Path | None = None,
    output_to_console: bool = True,
    output_to_file: bool = True,
    max_file_size_mb: int = 10,
    backup_count: int = 5,
) -> LoggingProfile:
    """
    Create a custom logging profile with specified parameters.

    Args:
        log_level: Minimum log level (string or LogLevel enum)
        use_json: Whether to use JSON format
        log_file: Custom log file path (defaults to logs/aigenflow.log)
        output_to_console: Enable console logging
        output_to_file: Enable file logging
        max_file_size_mb: Maximum file size before rotation (MB)
        backup_count: Number of backup files to keep

    Returns:
        Custom LoggingProfile configuration

    Examples:
        >>> # Custom profile for verbose debugging
        >>> profile = create_custom_profile(
        ...     "DEBUG",
        ...     use_json=False,
        ...     output_to_file=False,
        ... )

        >>> # Production-like custom profile
        >>> profile = create_custom_profile(
        ...     LogLevel.ERROR,
        ...     log_file=Path("var/critical.log"),
        ...     max_file_size_mb=50,
        ... )
    """
    if isinstance(log_level, str):
        log_level = LogLevel.from_string(log_level)

    targets = []
    if output_to_console:
        targets.append("console")
    if output_to_file:
        targets.append("file")

    return LoggingProfile(
        name="custom",
        log_level=log_level,
        output_targets=tuple(targets),
        use_json=use_json,
        log_file_path=log_file or _get_default_log_file(),
        max_file_size_mb=max_file_size_mb,
        backup_count=backup_count,
    )

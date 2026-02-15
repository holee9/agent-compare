"""
Logging configuration for AigenFlow pipeline.
"""

import logging
import re
import sys
from pathlib import Path
from typing import Any

import structlog

_SENSITIVE_KEYWORDS = (
    "key",
    "token",
    "secret",
    "password",
    "passwd",
    "cookie",
    "auth",
    "authorization",
    "session",
)
_LONG_SECRET_PATTERN = re.compile(r"[A-Za-z0-9_\-]{20,}")


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(keyword in lowered for keyword in _SENSITIVE_KEYWORDS)


def _mask_string(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        return value
    if len(stripped) <= 8:
        return "***"
    return f"{stripped[:4]}...{stripped[-4:]}"


def redact_secrets(value: Any, key_hint: str | None = None) -> Any:
    """Recursively redact sensitive values in logs."""
    if isinstance(value, dict):
        return {k: redact_secrets(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_secrets(item, key_hint) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_secrets(item, key_hint) for item in value)
    if isinstance(value, str):
        if key_hint and _is_sensitive_key(key_hint):
            return _mask_string(value)
        if _LONG_SECRET_PATTERN.fullmatch(value.strip()):
            return _mask_string(value)
        return value
    return value


def redact_event_dict(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    return redact_secrets(event_dict)


def setup_logging(level: int | str = logging.INFO, log_file: Path | None = None, json_logs: bool = False) -> None:
    processors = [
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        redact_event_dict,
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())

    shared_processors = processors.copy()

    console_processors = shared_processors.copy()
    if not json_logs:
        console_processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=shared_processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logger = structlog.get_logger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(level)

    return logger


def get_logger(name: str | None = None) -> Any:
    logger_name = name or "aigenflow"
    return structlog.get_logger(logger_name)


class LogContext:
    def __init__(self, **context: Any) -> None:
        self._context = context
        self._logger = structlog.get_logger()

    def __enter__(self) -> Any:
        return self._logger.bind(**self._context)

    def __exit__(self, *args: Any) -> None:
        pass

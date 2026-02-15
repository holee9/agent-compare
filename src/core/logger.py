"""
Logging configuration for agent-compare pipeline.
"""

import logging
import sys
from pathlib import Path
from typing import Any

import structlog


def setup_logging(level: int | str = logging.INFO, log_file: Path | None = None, json_logs: bool = False) -> None:
    processors = [
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
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
    logger_name = name or "agent-compare"
    return structlog.get_logger(logger_name)


class LogContext:
    def __init__(self, **context: Any) -> None:
        self._context = context
        self._logger = structlog.get_logger()

    def __enter__(self) -> Any:
        return self._logger.bind(**self._context)

    def __exit__(self, *args: Any) -> None:
        pass

"""
Resilience modules for error recovery and fault tolerance.

This module provides:
- FallbackChain: Automatic AI provider fallback on failure
- CircuitBreaker: Circuit breaker pattern for provider health
- FailureDetector: Detect and classify failures
"""

from .fallback_chain import (
    FallbackChain,
    FallbackConfig,
    FallbackContext,
    FallbackDecision,
    FallbackReason,
)

__all__ = [
    "FallbackChain",
    "FallbackConfig",
    "FallbackContext",
    "FallbackDecision",
    "FallbackReason",
]

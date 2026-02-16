"""
AigenFlow - Multi-AI Pipeline CLI Tool for Automated Business Plan Generation.

This package provides a unified CLI interface for orchestrating AI agents
across multiple providers to generate comprehensive business plans.
"""

__version__ = "0.1.0"
__author__ = "drake"
__license__ = "Apache-2.0"

# Lazy import - only import app when actually needed
# This avoids import errors during package initialization
def _get_app():
    """Lazy load the app function."""
    import sys
    from pathlib import Path

    # Find src directory relative to this file
    here = Path(__file__).parent
    src_dir = here.parent

    # Add to path if not already there
    src_str = str(src_dir)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)

    from src.main import app
    return app

# Make app available as a property-like access
class _AppLazy:
    """Lazy loader for app to avoid import errors."""
    def __call__(self):
        return _get_app()

app = _AppLazy()

__all__ = ["app", "__version__"]

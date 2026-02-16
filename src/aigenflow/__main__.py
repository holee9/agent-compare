"""
Main entry point for `python -m aigenflow` execution.
"""
import sys
from pathlib import Path

# Setup path BEFORE any other imports
_here = Path(__file__).resolve()
_src_dir = _here.parent.parent
_src_str = str(_src_dir)
if _src_str not in sys.path:
    sys.path.insert(0, _src_str)

from src.main import app  # noqa: E402

if __name__ == "__main__":
    app()

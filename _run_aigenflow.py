#!/usr/bin/env python
"""
AigenFlow CLI launcher script.

This script provides a convenient way to run aigenflow without installation.
Usage: python aigenflow.py [options]
"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from src.main import app
app()

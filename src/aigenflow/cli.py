"""
CLI entry point for the aigenflow console command.

This module provides the entry point for the 'aigenflow' console script
installed by pip. It handles the module loading manually to work around
Python import system limitations with the src/ directory structure.
"""

import importlib.util
import sys
from pathlib import Path


def _load_src_main():
    """
    Load src.main module dynamically.

    This is necessary because the src/ directory structure doesn't
    conform to standard Python package layout, and editable installs
    don't properly set up the import path for console scripts.

    Returns:
        The src.main module with the app attribute.
    """
    # Get the src directory relative to this file
    # cli.py is at src/aigenflow/cli.py
    # So src is the parent of the aigenflow directory
    here = Path(__file__).resolve()
    src_dir = here.parent.parent

    # Load main.py directly
    main_path = src_dir / "main.py"
    spec = importlib.util.spec_from_file_location("src.main", main_path)
    module = importlib.util.module_from_spec(spec)

    # Set up sys.modules for proper importing of dependencies
    # Create a pseudo src package
    src_package = type(sys)("src")
    src_package.__path__ = [str(src_dir)]
    src_package.__file__ = str(src_dir / "__init__.py")

    sys.modules["src"] = src_package
    sys.modules["src.main"] = module

    # Execute the module (this runs all the imports in main.py)
    spec.loader.exec_module(module)

    return module


def main():
    """
    Main CLI entry point.

    This function is called by the 'aigenflow' console script.
    """
    main_module = _load_src_main()
    app = main_module.app
    app()


# Export for convenience
__all__ = ["main"]

"""
Tests for CLI layer.
"""

import pytest


class TestCLI:
    """Tests for CLI application."""

    def test_main_function_exists(self):
        """Test that main function exists."""
        from main import main

        assert main is not None
        assert callable(main)

    def test_main_execution(self):
        """Test main execution doesn't crash."""
        from main import main

        # Just test that main can be called without error
        # (it will print help and exit normally)
        try:
            main()
        except SystemExit:
            # Expected - typer Exit raises SystemExit
            pass

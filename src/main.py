"""
Main CLI entry point for AigenFlow.

Provides unified CLI interface for all commands.
"""

import sys
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import typer
from rich.console import Console
from rich.table import Table

from config.logging_profiles import (
    LogEnvironment,
    LogLevel,
    create_custom_profile,
    get_logging_profile,
)
from core import get_settings, get_logger
from core.logger import setup_logging

# Import CLI command apps
from cli.check import app as check_app
from cli.config import app as config_app
from cli.relogin import app as relogin_app
from cli.resume import app as resume_app
from cli.setup import app as setup_app
from cli.status import app as status_app

console = Console()

# Create main Typer app
app = typer.Typer(
    help="AigenFlow - Multi-AI Pipeline CLI Tool for Automated Business Plan Generation",
    no_args_is_help=True,
    add_completion=False,
)


def _configure_logging(
    log_level: str | None = None,
    log_file: Path | None = None,
) -> None:
    """
    Configure logging based on CLI options or environment settings.

    Args:
        log_level: Optional log level from CLI (debug, info, warning, error)
        log_file: Optional custom log file path
    """
    settings = get_settings()

    # Determine log level
    if log_level:
        try:
            level = LogLevel.from_string(log_level)
            profile = create_custom_profile(
                level,
                log_file=log_file,
                output_to_console=True,
                output_to_file=True,
            )
            setup_logging(profile=profile)
            return
        except ValueError as e:
            console.print(f"[bold red]Invalid log level: {e}[/bold red]")
            raise typer.Exit(code=1)

    # Use environment-based profile
    environment = (
        LogEnvironment.DEVELOPMENT
        if settings.debug
        else LogEnvironment.PRODUCTION
    )
    profile = get_logging_profile(environment)

    # Override log file if provided
    if log_file:
        profile = create_custom_profile(
            profile.log_level,
            log_file=log_file,
            output_to_console=profile.should_log_to_console(),
            output_to_file=True,
            use_json=profile.use_json,
        )

    setup_logging(profile=profile)

    logger = get_logger("aigenflow.cli")
    logger.info(
        "Logging configured",
        environment=environment.value,
        log_level=profile.log_level.value,
        log_file=str(profile.log_file_path),
    )


# Preserve existing run command behavior
def _preserve_run_command():
    """Preserve the original run command for backward compatibility."""
    console.print("[bold green]aigenflow v0.1.0[/bold green]")
    console.print("Multi-AI Pipeline CLI Tool for Automated Business Plan Generation")
    console.print("")
    console.print("[dim]Usage:[/dim]")
    console.print("[dim]  aigenflow run --topic \"Your topic here\"[/dim]")
    console.print("")
    console.print("[bold cyan]Options:[/bold cyan]")
    console.print("  run        Execute pipeline and generate document")
    console.print("  check       Check AI provider sessions")
    console.print("              --topic    Document topic (required)")
    console.print("              --type      Document type: bizplan or rd (default: bizplan)")
    console.print("              --template  Template name (default, startup, strategy)")
    console.print("              --lang      Output language (ko or en)")
    console.print("")


# Main command (default when no subcommand is provided)
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
    log_level: str | None = typer.Option(
        None,
        "--log-level",
        help="Set logging level (debug, info, warning, error)",
    ),
    log_file: Path | None = typer.Option(
        None,
        "--log-file",
        help="Custom log file path (default: logs/aigenflow.log)",
    ),
) -> None:
    """
    AigenFlow CLI main entry point.
    """
    # Configure logging before any other operations
    _configure_logging(log_level, log_file)

    if version:
        console.print("[bold green]aigenflow v0.1.0[/bold green]")
        raise typer.Exit()

    # If no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        _preserve_run_command()


# Register all CLI commands as subcommands
app.add_typer(check_app, name="check", help="Check Playwright browser and AI provider sessions")
app.add_typer(setup_app, name="setup", help="Interactive setup wizard for first-time configuration")
app.add_typer(relogin_app, name="relogin", help="Re-authenticate with AI providers")
app.add_typer(status_app, name="status", help="Display pipeline execution status")
app.add_typer(resume_app, name="resume", help="Resume interrupted pipeline execution")
app.add_typer(config_app, name="config", help="Manage configuration settings")


if __name__ == "__main__":
    app()

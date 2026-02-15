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

from core import get_settings

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
) -> None:
    """
    AigenFlow CLI main entry point.
    """
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

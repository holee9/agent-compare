"""
Main CLI entry point for AigenFlow.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typer import Exit
from rich.console import Console

from src.core import get_settings


def main():
    """Main CLI entry point."""
    console = Console()

    # Simple greeting for now
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


if __name__ == "__main__":
    main()

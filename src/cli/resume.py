"""
Resume command for AigenFlow CLI.

Resume interrupted pipeline execution.
"""

import json
import sys
from pathlib import Path

import typer
from rich.console import Console

console = Console()

# Sessions directory
SESSIONS_DIR = Path("output") / "sessions"


app = typer.Typer(help="Resume pipeline")


@app.command()
def resume(
    session_id: str = typer.Argument(..., help="Pipeline session ID to resume"),
) -> None:
    """
    Resume an interrupted pipeline execution.

    Examples:
        aigenflow resume abc-123-def
    """
    # Ensure sessions directory exists
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    # Check if session file exists
    session_file = SESSIONS_DIR / f"session_{session_id}.json"
    if not session_file.exists():
        console.print(f"[red]✗ Session not found: {session_id}[/red]")
        console.print("\n[bold]Available sessions:[/bold]")
        session_files = list(SESSIONS_DIR.glob("session_*.json"))
        if session_files:
            for sf in session_files[:5]:
                sid = sf.stem.replace("session_", "")
                console.print(f"  - {sid}")
        else:
            console.print("  No sessions available")
        sys.exit(1)

    # Load session
    with open(session_file) as f:
        session_data = json.load(f)

    console.print(f"[bold cyan]Resuming session:[/bold cyan] {session_id}")
    console.print(f"[bold]Phase:[/bold] {session_data['phase']}")
    console.print(f"[bold]Status:[/bold] {session_data['status']}\n")

    # TODO: Implement actual resume logic
    console.print("[yellow]Resume functionality is under development[/yellow]")
    console.print("[yellow]The session data has been loaded successfully.[/yellow]")


if __name__ == "__main__":
    typer.run(app)

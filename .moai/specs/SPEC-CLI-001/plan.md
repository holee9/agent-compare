# Implementation Plan - SPEC-CLI-001

---
spec_id: SPEC-CLI-001
title: Fix AigenFlow CLI Run Command
created: 2026-02-16
status: Planned
priority: P0
---

## Implementation Milestones

### Priority Ordering

**Priority High (P0) - Release Blockers:**
- Milestone 1: Create run command skeleton
- Milestone 2: Implement input validation
- Milestone 3: Integrate with orchestrator
- Milestone 4: Add error handling and edge cases

**Priority Medium (P1) - Quality Improvements:**
- Milestone 5: Add progress feedback
- Milestone 6: Implement configuration verification

**Priority Low (P2) - Future Enhancements:**
- Milestone 7: Improve resume command
- Milestone 8: Enhance config set command

---

## Milestone 1: Create Run Command Skeleton

### Objective
Create the basic `run` command structure following existing CLI patterns.

### Files to Create/Modify

**CREATE: src/cli/run.py**
- Import Click decorators
- Import Rich console
- Define run command with Click decorators
- Add basic docstring
- Register command parameters (--topic, --type, --language, --output)

**MODIFY: src/aigenflow/cli.py**
- Import run command from src.cli.run
- Register run command with Typer app
- Verify command appears in help output

### Implementation Steps

1. Create `src/cli/run.py` with Click command structure:
```python
import click
from rich.console import Console

console = Console()

@click.command()
@click.option('--topic', '-t', required=True, help='Topic for document generation')
@click.option('--type', '-y', 'doc_type', required=True,
              type=click.Choice(['bizplan', 'rd']),
              help='Document type (bizplan or rd)')
@click.option('--language', '-l', default='ko',
              type=click.Choice(['ko', 'en']),
              help='Output language (default: ko)')
@click.option('--output', '-o', default=None,
              help='Output directory override')
def run(topic: str, doc_type: str, language: str, output: str):
    """Generate business plan or R&D proposal document."""
    console.print("[bold blue]Starting generation...[/bold blue]")
    console.print(f"  Topic: {topic}")
    console.print(f"  Type: {doc_type}")
    console.print(f"  Language: {language}")
    # Placeholder - will be implemented in Milestone 3
    console.print("[yellow]Command structure created. Implementation pending.[/yellow]")
```

2. Modify `src/aigenflow/cli.py` to register run command:
```python
from ..cli.run import run

app.add_typer(run, name="run")
```

### Verification
- Run `aigenflow run --help` and verify command appears
- Run `aigenflow --help` and verify run is listed
- Verify parameter validation (choices for type and language)

### Success Criteria
- Command executes without "Missing command" error
- Help text displays correctly
- Parameter choices are enforced

---

## Milestone 2: Implement Input Validation

### Objective
Add comprehensive input validation for all parameters.

### Files to Modify

**MODIFY: src/cli/run.py**
- Add topic length validation
- Add custom error messages
- Add validation helper functions

### Implementation Steps

1. Create validation functions:
```python
def validate_topic(topic: str) -> str:
    """Validate topic meets minimum length requirement."""
    if len(topic) < 10:
        raise click.BadParameter(
            f"Topic must be at least 10 characters. Provided: {len(topic)} characters"
        )
    return topic

def validate_configuration():
    """Verify system is properly configured."""
    from ..core.config import settings
    if not settings.is_configured():
        raise click.ClickException(
            "System not configured. Please run 'aigenflow setup' first."
        )
```

2. Integrate validation into run command:
```python
@click.command()
@click.option('--topic', '-t', required=True, callback=validate_topic,
              help='Topic for document generation (min 10 characters)')
@click.option('--type', '-y', 'doc_type', required=True,
              type=click.Choice(['bizplan', 'rd']),
              help='Document type')
@click.option('--language', '-l', default='ko',
              type=click.Choice(['ko', 'en']),
              help='Output language')
@click.option('--output', '-o', default=None,
              help='Output directory override')
def run(topic: str, doc_type: str, language: str, output: str):
    """Generate business plan or R&D proposal document."""
    # Validate configuration
    validate_configuration()

    # Display validated parameters
    console.print("[bold blue]Starting generation...[/bold blue]")
    console.print(f"  Topic: {topic}")
    console.print(f"  Type: {doc_type}")
    console.print(f"  Language: {language}")
```

### Verification
- Test with topic < 10 characters: Should display error
- Test without running setup: Should prompt for setup
- Test with valid inputs: Should proceed

### Success Criteria
- All edge cases (EC-001 to EC-005) are handled
- Clear error messages with actionable guidance
- Exit codes are appropriate (1 for errors)

---

## Milestone 3: Integrate with Orchestrator

### Objective
Connect run command to the existing orchestrator for document generation.

### Files to Modify

**MODIFY: src/cli/run.py**
- Import orchestrator from src.main
- Import GenerationRequest model
- Call orchestrator.run_generation()
- Handle orchestrator responses

### Implementation Steps

1. Add orchestrator integration:
```python
from ..main import orchestrator
from ..core.models import GenerationRequest
from pathlib import Path

def run(topic: str, doc_type: str, language: str, output: str):
    """Generate business plan or R&D proposal document."""
    validate_configuration()

    console.print("[bold blue]Starting generation...[/bold blue]")
    console.print(f"  Topic: {topic}")
    console.print(f"  Type: {doc_type}")
    console.print(f"  Language: {language}")

    try:
        # Create generation request
        request = GenerationRequest(
            topic=topic,
            doc_type=doc_type,
            language=language,
            output_dir=Path(output) if output else None
        )

        # Execute generation
        with console.status("[bold green]Generating document...[/bold green]"):
            result = orchestrator.run_generation(request)

        # Display results
        console.print("[bold green]Generation complete![/bold green]")
        console.print(f"  Session ID: {result.session_id}")
        console.print(f"  Output: {result.output_path}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.ClickException(f"Generation failed: {str(e)}")
```

### Verification
- Test business plan generation: `aigenflow run --topic "AI-powered content generation platform" --type bizplan`
- Test R&D proposal generation: `aigenflow run --topic "Machine learning model for sentiment analysis" --type rd`
- Verify output files are created

### Success Criteria
- REQ-001: Business plan generation works
- REQ-002: R&D proposal generation works
- Output files are created in correct directory
- Session ID is displayed for resume capability

---

## Milestone 4: Add Error Handling and Edge Cases

### Objective
Implement comprehensive error handling for all identified edge cases.

### Files to Modify

**MODIFY: src/cli/run.py**
- Add session validation
- Add expired session handling
- Add output directory conflict handling
- Add interrupt signal handling
- Add timeout handling

### Implementation Steps

1. Add session validation:
```python
def validate_sessions():
    """Verify AI sessions are valid and not expired."""
    from ..core.config import settings
    if not settings.has_valid_sessions():
        if settings.has_expired_sessions():
            raise click.ClickException(
                "AI sessions have expired. Please run 'aigenflow relogin' to refresh."
            )
        else:
            raise click.ClickException(
                "No valid AI sessions found. Please run 'aigenflow setup' to configure."
            )
```

2. Add output directory handling:
```python
def check_output_directory(output_path: Path):
    """Check if output directory exists and warn user."""
    if output_path.exists():
        console.print(
            "[yellow]Warning: Output directory already exists. "
            "Files may be overwritten.[/yellow]"
        )
```

3. Add interrupt handling:
```python
import signal

def handle_interrupt(signum, frame):
    """Handle Ctrl+C gracefully."""
    console.print("\n[yellow]Generation interrupted by user.[/yellow]")
    console.print("Use 'aigenflow resume --session-id SESSION_ID' to continue.")
    raise click.Abort()

signal.signal(signal.SIGINT, handle_interrupt)
```

4. Add timeout handling:
```python
import asyncio
from asyncio import TimeoutError

async def run_with_timeout(request: GenerationRequest, timeout_minutes: int = 30):
    """Execute generation with timeout."""
    try:
        result = await asyncio.wait_for(
            orchestrator.run_generation_async(request),
            timeout=timeout_minutes * 60
        )
        return result
    except TimeoutError:
        raise click.ClickException(
            f"Generation timed out after {timeout_minutes} minutes. "
            "Use 'aigenflow resume --session-id SESSION_ID' to continue."
        )
```

### Verification
- Test EC-005: No valid sessions
- Test EC-006: Expired sessions
- Test EC-007: Existing output directory
- Test EC-008: Pipeline failure
- Test EC-009: Ctrl+C interrupt
- Test EC-010: Timeout scenario

### Success Criteria
- All edge cases handled gracefully
- Clear error messages with actionable guidance
- Resume capability information provided
- Appropriate exit codes

---

## Milestone 5: Add Progress Feedback

### Objective
Provide real-time progress feedback to users during generation.

### Files to Modify

**MODIFY: src/cli/run.py**
- Add progress callback
- Display phase progress
- Show completion status

### Implementation Steps

1. Create progress callback:
```python
def progress_callback(phase: str, status: str, progress: float):
    """Display progress updates."""
    console.print(f"  [{phase}] {status} ({progress:.0%})")
```

2. Integrate with orchestrator:
```python
result = orchestrator.run_generation(
    request,
    progress_callback=progress_callback
)
```

3. Add phase indicators:
```python
PHASES = {
    "init": "Initializing",
    "research": "Researching topic",
    "outline": "Creating outline",
    "draft": "Drafting content",
    "review": "Reviewing and refining",
    "finalize": "Finalizing document"
}
```

### Success Criteria
- Users see real-time progress
- Phase changes are clearly indicated
- Completion message includes output path

---

## Milestone 6: Implement Configuration Verification

### Objective
Add comprehensive configuration checks before generation.

### Files to Modify

**MODIFY: src/cli/run.py**
- Add detailed configuration validation
- Provide setup guidance
- Check all required settings

### Implementation Steps

1. Create detailed validation:
```python
def verify_configuration():
    """Verify all required configuration is present."""
    from ..core.config import settings

    issues = []

    if not settings.api_key:
        issues.append("API key not configured")

    if not settings.output_dir:
        issues.append("Output directory not set")

    if not settings.has_valid_sessions():
        issues.append("No valid AI sessions")

    if issues:
        console.print("[bold red]Configuration issues found:[/bold red]")
        for issue in issues:
            console.print(f"  - {issue}")
        console.print("\nRun 'aigenflow setup' to configure the system.")
        raise click.ClickException("Configuration incomplete")
```

### Success Criteria
- All configuration issues are detected
- Clear guidance provided for resolution
- Setup command recommended

---

## Technical Approach

### Architecture Pattern

Follow the existing CLI command pattern established in `setup.py` and `status.py`:

```
User Input → Click Validation → Configuration Check → Orchestrator Call → Output
```

### Error Handling Strategy

1. **Input Validation Errors:**
   - Use Click's BadParameter for parameter errors
   - Provide clear, actionable error messages
   - Include examples in error messages

2. **Configuration Errors:**
   - Use ClickException for system errors
   - Direct users to setup or relogin commands
   - List all missing configuration items

3. **Runtime Errors:**
   - Catch and wrap orchestrator exceptions
   - Preserve session ID for resume capability
   - Log errors with context for debugging

### Testing Strategy

1. **Unit Tests:**
   - Test each validation function independently
   - Test error message formatting
   - Test edge case handling

2. **Integration Tests:**
   - Test orchestrator integration
   - Test configuration validation
   - Test end-to-end generation

3. **Manual Testing:**
   - Test all CLI command variations
   - Test interrupt handling
   - Test error scenarios

---

## Risk Assessment

### Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Orchestrator API changes | Low | High | Check orchestrator interface before implementation |
| Configuration model mismatch | Low | Medium | Verify settings structure matches existing code |
| Import path issues | Medium | Low | Follow existing import patterns exactly |
| Click decorator incompatibility | Low | Medium | Reference existing working commands |
| Rich console formatting issues | Low | Low | Use standard Rich patterns |

### Mitigation Plan

1. **Before Implementation:**
   - Read src/main.py to understand orchestrator interface
   - Read src/core/models.py to understand GenerationRequest
   - Read src/cli/setup.py for CLI pattern reference

2. **During Implementation:**
   - Implement incrementally (Milestone 1 → 4)
   - Test each milestone before proceeding
   - Keep changes minimal and focused

3. **After Implementation:**
   - Run full test suite
   - Perform manual CLI testing
   - Update README.md if needed

---

## Dependencies

### Internal Dependencies
- `src/main.py` - Orchestrator module
- `src/core/models.py` - GenerationRequest model
- `src/core/config.py` - Settings and configuration
- `src/cli/setup.py` - Reference pattern
- `src/cli/status.py` - Reference pattern

### External Dependencies
- `click` - CLI framework (already installed)
- `rich` - Console output (already installed)
- `pathlib` - Path handling (standard library)

---

## Success Metrics

### Functional Metrics
- All P0 requirements implemented
- All edge cases handled
- Command executes without errors
- Documents generated successfully

### Quality Metrics
- Test coverage ≥ 85%
- Zero linter errors
- Zero type errors
- All TRUST 5 gates passed

### User Experience Metrics
- Clear error messages
- Helpful guidance in errors
- Progress feedback during generation
- Resume capability supported

---

## Next Steps

1. **Immediate (P0):**
   - Implement Milestone 1: Create run command skeleton
   - Implement Milestone 2: Add input validation
   - Implement Milestone 3: Integrate with orchestrator
   - Implement Milestone 4: Add error handling

2. **Short-term (P1):**
   - Implement Milestone 5: Add progress feedback
   - Implement Milestone 6: Configuration verification

3. **Medium-term (P2):**
   - Improve resume command (REQ-008)
   - Enhance config set command (REQ-009)

4. **Documentation:**
   - Update README.md if CLI usage changes
   - Add CLI reference documentation
   - Create troubleshooting guide

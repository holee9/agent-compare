# Architectural Design: CLI Run Command Implementation

**Team**: moai-plan-cli-fix
**Architect**: team-architect
**Date**: 2026-02-16

## 1. Problem Analysis

### Identified Gaps

1. **Missing `run` command**: No `src/cli/run.py` file exists
2. **Main CLI not registering run command**: `src/main.py` only has `app.add_typer()` for other commands
3. **Setup/status commands show help text referencing `run`** but command doesn't exist
4. **Resume command**: Has TODO comment for actual implementation

### Root Cause

The run command was planned but never implemented. The architecture supports it (orchestrator exists), but CLI entry point is missing.

---

## 2. Implementation Approach Comparison

### Option A: New `run.py` Subcommand Module (RECOMMENDED)

**File**: `src/cli/run.py`

**Pros**:
- Consistent with existing CLI structure (all commands are separate modules)
- Clear separation of concerns
- Easy to test independently
- Follows established patterns

**Cons**:
- One additional file to maintain

**Complexity**: Low

### Option B: Inline `run` Command in `main.py`

**Location**: Directly in `src/main.py`

**Pros**:
- All commands visible in one file
- Slightly fewer files

**Cons**:
- Breaks established pattern
- `main.py` becomes cluttered
- Harder to test independently
- Violates single responsibility principle

**Complexity**: Low

### Option C: Hybrid with Run as Direct Command

**Approach**: `@app.command()` instead of `app.add_typer()`

**Pros**:
- Simpler for single command scenarios

**Cons**:
- Inconsistent with other commands
- Harder to extend with `run` subcommands in future
- Mixes patterns

**Complexity**: Low

---

## 3. Recommended Approach: Option A

**Rationale**:
1. Consistency with existing CLI structure (8 other commands use this pattern)
2. Clean separation of concerns
3. Easier testing and maintenance
4. Future extensibility (could add `run --dry-run`, `run --continue`, etc.)

---

## 4. File Impact Analysis

### Files to Create

| File | Purpose | Lines (est.) |
|------|---------|--------------|
| `src/cli/run.py` | Main run command implementation | ~150 |

### Files to Modify

| File | Changes | Lines Modified |
|------|---------|----------------|
| `src/main.py` | Import and register run_app | ~5 |
| `tests/cli/test_run.py` | New test file for run command | ~100 |

### Files to Review (No Changes)

| File | Purpose |
|------|---------|
| `src/pipeline/orchestrator.py` | Contains `run_pipeline()` to call |
| `src/core/models.py` | Contains `PipelineConfig` to use |
| `src/core/config.py` | Contains `get_settings()` |

---

## 5. Implementation Design

### 5.1 `src/cli/run.py` Structure

```python
"""
Run command for AigenFlow CLI.

Execute the full pipeline to generate documents.
"""

import asyncio
import sys
from pathlib import Path

import typer
from rich.console import Console

from core import get_settings
from core.models import DocumentType, PipelineConfig, TemplateType
from pipeline.orchestrator import PipelineOrchestrator
from templates.manager import TemplateManager
from gateway.session import SessionManager

app = typer.Typer(help="Execute pipeline")
console = Console()


@app.command()
def run(
    topic: str = typer.Option(..., "--topic", "-t", help="Document topic (min 10 characters)"),
    doc_type: str = typer.Option("bizplan", "--type", help="Document type: bizplan or rd"),
    template: str = typer.Option("default", "--template", help="Template: default, startup, strategy, rd"),
    lang: str = typer.Option("ko", "--lang", "-l", help="Output language (ko or en)"),
    output_dir: Path = typer.Option(None, "--output", "-o", help="Custom output directory"),
    headed: bool = typer.Option(False, "--headed", help="Use headed browser mode"),
) -> None:
    """
    Execute the AigenFlow pipeline to generate a document.

    Examples:
        aigenflow run --topic "AI-powered fitness app for busy professionals"
        aigenflow run -t "Smart home automation system" --type rd --template strategy
        aigenflow run -t "E-commerce platform" --lang en --output ./my-output
    """
    # Validate and convert enum types
    # Create PipelineConfig
    # Initialize orchestrator with UI enabled
    # Run async pipeline
    # Handle errors and exit codes
```

### 5.2 `src/main.py` Changes

```python
# Add import
from src.cli.run import app as run_app

# Register run command (add around line 103)
app.add_typer(run_app, name="run", help="Execute pipeline and generate document")
```

### 5.3 Error Handling Strategy

1. **Validation errors**: Show user-friendly message with correct syntax
2. **Session errors**: Guide user to run `aigenflow setup` or `aigenflow relogin`
3. **Pipeline errors**: Save partial results before exit
4. **Browser errors**: Suggest `playwright install chromium`

---

## 6. Interface Contracts

### 6.1 CLI Arguments → PipelineConfig Mapping

| CLI Arg | Type | PipelineConfig Field | Validation |
|---------|------|---------------------|------------|
| `--topic` | str | `topic` | Min 10 chars, required |
| `--type` | str | `doc_type` | "bizplan" or "rd" |
| `--template` | str | `template` | "default", "startup", "strategy", "rd" |
| `--lang` | str | `language` | "ko" or "en" |
| `--output` | Path | `output_dir` | Must exist or create |
| `--headed` | bool | N/A | Pass to settings |

### 6.2 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Validation error |
| 3 | Session error |

---

## 7. Testing Strategy

### 7.1 Unit Tests (DDD Approach)

1. **Argument parsing tests**
   - Valid arguments parse correctly
   - Invalid arguments show helpful errors
   - Default values applied correctly

2. **Integration tests**
   - Mock orchestrator to verify correct parameters
   - Test error handling paths

3. **End-to-end tests**
   - Run with test configuration
   - Verify output files created

### 7.2 Test Coverage Targets

- New code (`run.py`): 85%+ coverage
- Modified code (`main.py`): Existing tests pass

---

## 8. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Async/sync mismatch | Medium | Proper `asyncio.run()` wrapper |
| Enum validation | Low | Field validators already exist |
| Path handling | Low | Use Path with `mkdir(parents=True)` |
| Session state | Medium | Check sessions before pipeline |
| Browser timeout | Medium | Settings timeout already configured |

---

## 9. Implementation Order

1. Create `src/cli/run.py` with basic structure
2. Add import and registration in `src/main.py`
3. Implement argument validation
4. Implement async pipeline execution
5. Add error handling
6. Create tests in `tests/cli/test_run.py`
7. Verify all tests pass
8. Manual testing with real scenarios

---

## 10. Rollout Plan

### Phase 1: Implementation
- Create files as designed
- All changes backward compatible

### Phase 2: Testing
- Run existing test suite (ensure no regressions)
- Add new tests for run command
- Manual testing with real pipeline

### Phase 3: Documentation
- Update README with run command examples
- Add CLI reference

### Backward Compatibility
- No breaking changes
- Existing commands unaffected
- New command is additive only

---

## 11. Additional Considerations

### 11.1 Resume Command TODO
The resume command has a TODO comment for actual implementation. This should be tracked as a separate task after run command is complete.

### 11.2 Setup Command Help Text
The setup command shows `Run 'aigenflow status' to see pipeline status` which is correct. No changes needed.

### 11.3 Status Command Help Text
Shows `aigenflow run <prompt>` which should become `aigenflow run --topic <prompt>` for consistency with CLI patterns.

---

## 12. Summary

**Recommended Implementation**: Create new `src/cli/run.py` following existing patterns

**Files Changed**: 1 modified, 1 created, 1 test file created

**Estimated Complexity**: Low

**Backward Compatible**: Yes

**Testing Approach**: DDD (characterization tests for existing, TDD for new)

**Next Steps**: Delegate to backend-dev for implementation

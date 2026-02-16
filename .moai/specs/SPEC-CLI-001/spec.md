# SPEC-CLI-001: Fix AigenFlow CLI Run Command

---
spec_id: SPEC-CLI-001
title: Fix AigenFlow CLI Run Command - Implement Missing Core Feature
created: 2026-02-16
status: Planned
priority: P0
assigned: manager-ddd
related_specs: []
epic: CLI Reliability
estimated_effort: 2-3 hours
labels: [cli, bug-fix, critical, user-facing]
lifecycle_level: spec-first
---

## Problem Analysis

### Root Cause Analysis (Five Whys)

1. **Surface Problem**: Users cannot generate business plans or R&D proposals using `aigenflow run` command
2. **First Why**: The command returns "Missing command" error
3. **Second Why**: `src/cli/run.py` file does not exist in the codebase
4. **Third Why**: The `run` command was never implemented despite being documented in README.md
5. **Fourth Why**: Gap between documentation and implementation during initial development
6. **Root Cause**: Incomplete CLI implementation - documented feature missing from codebase

### Assumptions

| Assumption | Confidence | Evidence | Risk if Wrong | Validation |
|------------|------------|----------|---------------|------------|
| Orchestrator.run_generation() exists and works | High | Codebase analysis shows src/main.py with orchestrator | Blocker | Verify by reading src/main.py |
| Existing CLI commands follow consistent pattern | High | setup.py and status.py show pattern | Minor inconsistency | Compare setup.py and status.py |
| Click is the CLI framework | High | setup.py uses @app.command() decorator | Framework mismatch | Verify Click imports |
| Models and settings are functional | High | Codebase shows src/core/models.py and config.py | Integration failure | Check imports in existing commands |

### Constraints

**Hard Constraints:**
- Must use Click CLI framework (existing pattern)
- Must integrate with existing orchestrator
- Must follow existing error handling patterns
- Must support Python 3.13+

**Soft Constraints:**
- Should match README.md documentation
- Should follow existing CLI command naming conventions
- Should provide helpful error messages

---

## Requirements (EARS Format)

### P0 - Critical Requirements (Release Blockers)

#### REQ-001: Business Plan Generation
**Type:** Event-Driven
**Pattern:** WHEN [user executes `aigenflow run --topic "topic" --type bizplan`] THEN [system shall generate business plan document]

**The system shall** generate a business plan document when the user provides:
- A valid topic string (minimum 10 characters)
- Type parameter set to "bizplan"
- Optional language parameter (default: "ko")

**Acceptance Criteria:**
- Command executes without "Missing command" error
- Orchestrator.run_generation() is called with correct parameters
- Output directory is created with session ID
- Generated files are written to output directory

#### REQ-002: R&D Proposal Generation
**Type:** Event-Driven
**Pattern:** WHEN [user executes `aigenflow run --topic "topic" --type rd`] THEN [system shall generate R&D proposal document]

**The system shall** generate an R&D proposal document when the user provides:
- A valid topic string (minimum 10 characters)
- Type parameter set to "rd"
- Optional language parameter (default: "ko")

**Acceptance Criteria:**
- Command executes without "Missing command" error
- Orchestrator.run_generation() is called with correct parameters
- Output directory is created with session ID
- Generated files are written to output directory

### P0 - Input Validation Requirements

#### REQ-003: Topic Validation
**Type:** State-Driven
**Pattern:** IF [topic is missing or shorter than 10 characters] THEN [system shall display error message and exit with code 1]

**The system shall** validate topic input:
- IF topic is missing: Display "Error: --topic is required" and exit
- IF topic length < 10: Display "Error: Topic must be at least 10 characters" and exit

#### REQ-004: Type Validation
**Type:** State-Driven
**Pattern:** IF [type is not 'bizplan' or 'rd'] THEN [system shall display error message with valid options and exit with code 1]

**The system shall** validate type parameter:
- IF type not in ["bizplan", "rd"]: Display "Error: --type must be 'bizplan' or 'rd'" and exit

#### REQ-005: Language Validation
**Type:** State-Driven
**Pattern:** IF [language is not 'ko' or 'en'] THEN [system shall display error message with valid options and exit with code 1]

**The system shall** validate language parameter:
- IF language not in ["ko", "en"]: Display "Error: --language must be 'ko' or 'en'" and exit

### P1 - High Priority Requirements

#### REQ-006: First-Time Setup Verification
**Type:** State-Driven
**Pattern:** IF [settings are not configured] THEN [system shall prompt user to run 'aigenflow setup' first]

**The system shall** check configuration:
- Verify API keys are set
- Verify output directory is accessible
- Prompt for setup if configuration is incomplete

#### REQ-007: Progress Feedback
**Type:** Event-Driven
**Pattern:** WHEN [generation is in progress] THEN [system shall display progress indicators to user]

**The system shall** provide user feedback:
- Display "Starting generation..." message
- Show progress spinner or status updates
- Display completion message with output path

### P2 - Medium Priority Requirements

#### REQ-008: Resume Pipeline (Improvement)
**Type:** Event-Driven
**Pattern:** WHEN [user executes `aigenflow resume --session-id ID`] THEN [system shall resume interrupted generation]

**The system shall** support resumption:
- Accept session-id parameter
- Load session state from output directory
- Continue from last successful phase

#### REQ-009: Config Set (Improvement)
**Type:** Event-Driven
**Pattern:** WHEN [user executes `aigenflow config set KEY VALUE`] THEN [system shall update configuration]

**The system shall** support configuration updates:
- Validate configuration key
- Update settings file
- Display confirmation message

---

## Edge Case Handling

### EC-001: Missing Topic Parameter
**Scenario:** User runs `aigenflow run --type bizplan` without --topic
**Expected:** Error message: "Error: --topic is required. Usage: aigenflow run --topic 'your topic' --type bizplan"
**Exit Code:** 1

### EC-002: Short Topic
**Scenario:** User provides topic shorter than 10 characters
**Expected:** Error message: "Error: Topic must be at least 10 characters. Provided: X characters"
**Exit Code:** 1

### EC-003: Invalid Type
**Scenario:** User provides --type "invalid"
**Expected:** Error message: "Error: --type must be 'bizplan' or 'rd'. Provided: invalid"
**Exit Code:** 1

### EC-004: Invalid Language
**Scenario:** User provides --language "fr"
**Expected:** Error message: "Error: --language must be 'ko' or 'en'. Provided: fr"
**Exit Code:** 1

### EC-005: No Valid AI Sessions
**Scenario:** No AI sessions configured or all sessions expired
**Expected:** Error message: "Error: No valid AI sessions found. Please run 'aigenflow setup' to configure sessions."
**Exit Code:** 1

### EC-006: Expired Sessions
**Scenario:** Configured sessions have expired
**Expected:** Error message: "Error: AI sessions have expired. Please run 'aigenflow relogin' to refresh sessions."
**Exit Code:** 1

### EC-007: Output Directory Exists
**Scenario:** Output directory for session already exists
**Expected:** Warning message: "Warning: Output directory already exists. Files may be overwritten."
**Continue:** Yes (overwrite allowed)

### EC-008: Pipeline Failure
**Scenario:** Generation fails mid-process
**Expected:** Error message with failure reason and session ID for resume
**Exit Code:** 1

### EC-009: Interrupt Signal (Ctrl+C)
**Scenario:** User interrupts generation with Ctrl+C
**Expected:** Graceful shutdown message with session ID for resume
**Exit Code:** 130 (SIGINT)

### EC-010: Timeout
**Scenario:** Generation exceeds maximum allowed time
**Expected:** Error message: "Error: Generation timed out after X minutes. Use 'aigenflow resume --session-id ID' to continue."
**Exit Code:** 1

---

## Technical Specifications

### File Structure

```
src/
├── cli/
│   ├── __init__.py
│   ├── run.py          # NEW - Run command implementation
│   ├── setup.py        # EXISTS - Reference pattern
│   └── status.py       # EXISTS - Reference pattern
├── aigenflow/
│   └── cli.py          # MODIFY - Register run command
├── main.py             # EXISTS - Orchestrator integration
├── core/
│   ├── models.py       # EXISTS - Data models
│   └── config.py       # EXISTS - Configuration
└── monitoring/
    └── stats.py        # EXISTS - Statistics tracking
```

### Command Registration Pattern

Based on existing `setup.py` and `status.py`:

```python
# src/cli/run.py
import click
from rich.console import Console
from ..main import orchestrator
from ..core.config import settings
from ..core.models import GenerationRequest

console = Console()

@click.command()
@click.option('--topic', '-t', required=True, help='Topic for document generation')
@click.option('--type', '-y', 'doc_type', required=True, type=click.Choice(['bizplan', 'rd']), help='Document type')
@click.option('--language', '-l', default='ko', type=click.Choice(['ko', 'en']), help='Output language')
@click.option('--output', '-o', default=None, help='Output directory override')
def run(topic: str, doc_type: str, language: str, output: str):
    """Generate business plan or R&D proposal document."""
    # Implementation
```

### Integration Points

1. **Orchestrator Integration:**
   - Import: `from ..main import orchestrator`
   - Call: `orchestrator.run_generation(request: GenerationRequest)`
   - Return: Session ID and output path

2. **Configuration Check:**
   - Import: `from ..core.config import settings`
   - Validate: `settings.is_configured()`
   - Prompt: Direct to `aigenflow setup` if not configured

3. **Error Handling:**
   - Use Rich console for formatted error messages
   - Exit with appropriate exit codes
   - Provide actionable error messages

---

## Quality Gates (TRUST 5)

### Tested
- Unit tests for run.py command
- Integration tests for orchestrator integration
- Edge case tests for all validation scenarios
- Coverage target: 85%+

### Readable
- Clear function and variable naming
- Docstrings for all functions
- Type hints for all parameters
- Follow existing CLI command patterns

### Unified
- Consistent with setup.py and status.py patterns
- Use Click decorators consistently
- Follow Rich console formatting patterns
- Match error message format

### Secured
- Input validation for all parameters
- No command injection vulnerabilities
- Secure handling of API keys
- Safe file path handling

### Trackable
- Session ID logging
- Generation status tracking
- Error logging with context
- Resume capability support

---

## Traceability

| Requirement | User Story | Implementation File | Test File |
|-------------|------------|---------------------|-----------|
| REQ-001 | US-001 | src/cli/run.py | tests/cli/test_run.py |
| REQ-002 | US-002 | src/cli/run.py | tests/cli/test_run.py |
| REQ-003 | EC-001, EC-002 | src/cli/run.py | tests/cli/test_run_validation.py |
| REQ-004 | EC-003 | src/cli/run.py | tests/cli/test_run_validation.py |
| REQ-005 | EC-004 | src/cli/run.py | tests/cli/test_run_validation.py |
| REQ-006 | US-003 | src/cli/run.py | tests/cli/test_run_integration.py |
| REQ-007 | US-001, US-002 | src/cli/run.py | tests/cli/test_run_feedback.py |
| REQ-008 | US-006 | src/cli/run.py | tests/cli/test_resume.py |
| REQ-009 | US-008 | src/cli/config.py | tests/cli/test_config.py |

---

## References

- README.md - CLI usage documentation
- src/cli/setup.py - Reference CLI command pattern
- src/cli/status.py - Reference CLI command pattern
- src/main.py - Orchestrator integration
- src/core/models.py - Data models
- Click documentation - https://click.palletsprojects.com/
- Rich documentation - https://rich.readthedocs.io/

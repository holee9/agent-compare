# Acceptance Criteria - SPEC-CLI-001

---
spec_id: SPEC-CLI-001
title: Fix AigenFlow CLI Run Command
created: 2026-02-16
status: Planned
priority: P0
---

## Acceptance Criteria (Given-When-Then Format)

### P0 - Critical User Stories

#### US-001: Business Plan Generation

**Scenario: Generate business plan with valid inputs**
```
GIVEN the user has run 'aigenflow setup' and configured API keys
AND the user has a topic for business plan generation
WHEN the user executes 'aigenflow run --topic "AI-powered content generation platform for enterprises" --type bizplan'
THEN the system should display "Starting generation..." message
AND the system should display progress indicators
AND the system should create an output directory with session ID
AND the system should generate business plan documents
AND the system should display "Generation complete!" with output path
AND the command should exit with code 0
```

**Scenario: Generate business plan in English**
```
GIVEN the user has configured the system
WHEN the user executes 'aigenflow run --topic "AI content platform" --type bizplan --language en'
THEN the system should generate documents in English
AND all output should be in English language
```

#### US-002: R&D Proposal Generation

**Scenario: Generate R&D proposal with valid inputs**
```
GIVEN the user has run 'aigenflow setup' and configured API keys
AND the user has a topic for R&D proposal
WHEN the user executes 'aigenflow run --topic "Machine learning model for sentiment analysis in social media" --type rd'
THEN the system should display "Starting generation..." message
AND the system should display progress indicators
AND the system should create an output directory with session ID
AND the system should generate R&D proposal documents
AND the system should display "Generation complete!" with output path
AND the command should exit with code 0
```

**Scenario: Generate R&D proposal with custom output directory**
```
GIVEN the user has configured the system
WHEN the user executes 'aigenflow run --topic "ML sentiment analysis" --type rd --output ./my-output'
THEN the system should use the specified output directory
AND documents should be created in ./my-output
```

---

### Input Validation Acceptance Criteria

#### AC-001: Missing Topic Parameter

```
GIVEN the user wants to generate a document
WHEN the user executes 'aigenflow run --type bizplan' without --topic
THEN the system should display error message: "Error: --topic is required"
AND the system should display usage hint
AND the command should exit with code 1
```

#### AC-002: Short Topic

```
GIVEN the user provides a topic shorter than 10 characters
WHEN the user executes 'aigenflow run --topic "AI" --type bizplan'
THEN the system should display error message: "Error: Topic must be at least 10 characters. Provided: 2 characters"
AND the command should exit with code 1
```

#### AC-003: Invalid Type

```
GIVEN the user provides an invalid document type
WHEN the user executes 'aigenflow run --topic "Valid topic string" --type invalid'
THEN the system should display error message: "Error: Invalid value for '--type': 'invalid' is not one of 'bizplan', 'rd'."
AND the command should exit with code 2 (Click validation error)
```

#### AC-004: Invalid Language

```
GIVEN the user provides an invalid language
WHEN the user executes 'aigenflow run --topic "Valid topic" --type bizplan --language fr'
THEN the system should display error message: "Error: Invalid value for '--language': 'fr' is not one of 'ko', 'en'."
AND the command should exit with code 2 (Click validation error)
```

---

### Configuration Acceptance Criteria

#### AC-005: System Not Configured

```
GIVEN the user has not run 'aigenflow setup'
WHEN the user executes 'aigenflow run --topic "Valid topic string" --type bizplan'
THEN the system should display error message: "Error: System not configured. Please run 'aigenflow setup' first."
AND the command should exit with code 1
```

#### AC-006: No Valid Sessions

```
GIVEN the user has run setup but sessions have not been created
WHEN the user executes 'aigenflow run --topic "Valid topic" --type bizplan'
THEN the system should display error message: "Error: No valid AI sessions found. Please run 'aigenflow setup' to configure."
AND the command should exit with code 1
```

#### AC-007: Expired Sessions

```
GIVEN the user has configured sessions but they have expired
WHEN the user executes 'aigenflow run --topic "Valid topic" --type bizplan'
THEN the system should display error message: "Error: AI sessions have expired. Please run 'aigenflow relogin' to refresh."
AND the command should exit with code 1
```

---

### Edge Case Acceptance Criteria

#### AC-008: Output Directory Exists

```
GIVEN the output directory for the session already exists
WHEN the user executes 'aigenflow run --topic "Valid topic" --type bizplan'
THEN the system should display warning: "Warning: Output directory already exists. Files may be overwritten."
AND the system should continue with generation
AND existing files should be overwritten
```

#### AC-009: Pipeline Failure

```
GIVEN the orchestrator encounters an error during generation
WHEN the generation fails mid-process
THEN the system should display error message with failure reason
AND the system should display session ID for resume
AND the command should exit with code 1
```

#### AC-010: User Interrupt (Ctrl+C)

```
GIVEN generation is in progress
WHEN the user presses Ctrl+C
THEN the system should display "Generation interrupted by user."
AND the system should display session ID for resume
AND the command should exit with code 130 (SIGINT)
```

#### AC-011: Generation Timeout

```
GIVEN generation takes longer than the timeout period
WHEN the timeout is reached
THEN the system should display error message: "Error: Generation timed out after 30 minutes. Use 'aigenflow resume --session-id SESSION_ID' to continue."
AND the command should exit with code 1
```

---

### P1 - High Priority Acceptance Criteria

#### AC-012: Progress Feedback

```
GIVEN generation is in progress
WHEN each phase completes
THEN the system should display phase name and status
AND the system should show progress percentage
AND the user should see real-time updates
```

**Example Output:**
```
Starting generation...
  [init] Initializing (10%)
  [research] Researching topic (25%)
  [outline] Creating outline (40%)
  [draft] Drafting content (60%)
  [review] Reviewing and refining (80%)
  [finalize] Finalizing document (100%)
Generation complete!
  Session ID: abc123
  Output: ./output/abc123/
```

#### AC-013: Detailed Configuration Validation

```
GIVEN multiple configuration items are missing
WHEN the user executes run command
THEN the system should list all missing items
AND the system should provide setup guidance
AND the command should exit with code 1
```

**Example Output:**
```
Configuration issues found:
  - API key not configured
  - Output directory not set
  - No valid AI sessions

Run 'aigenflow setup' to configure the system.
Error: Configuration incomplete
```

---

### P2 - Medium Priority Acceptance Criteria

#### AC-014: Resume Pipeline

```
GIVEN a generation was interrupted
WHEN the user executes 'aigenflow resume --session-id SESSION_ID'
THEN the system should load session state
AND the system should continue from last successful phase
AND the system should complete generation
```

#### AC-015: Config Set

```
GIVEN the user wants to update a configuration value
WHEN the user executes 'aigenflow config set output_dir ./new-output'
THEN the system should validate the key
AND the system should update the configuration file
AND the system should display confirmation: "Configuration updated: output_dir = ./new-output"
```

---

## Test Scenarios

### Unit Tests

#### Test Suite: test_run_validation.py

```python
import pytest
from click.testing import CliRunner
from src.cli.run import run, validate_topic

class TestTopicValidation:
    def test_missing_topic(self):
        """Test AC-001: Missing topic parameter"""
        runner = CliRunner()
        result = runner.invoke(run, ['--type', 'bizplan'])
        assert result.exit_code == 1
        assert '--topic is required' in result.output

    def test_short_topic(self):
        """Test AC-002: Topic shorter than 10 characters"""
        runner = CliRunner()
        result = runner.invoke(run, ['--topic', 'AI', '--type', 'bizplan'])
        assert result.exit_code == 1
        assert 'at least 10 characters' in result.output

    def test_valid_topic(self):
        """Test valid topic passes validation"""
        result = validate_topic("Valid topic with sufficient length")
        assert result == "Valid topic with sufficient length"

class TestTypeValidation:
    def test_invalid_type(self):
        """Test AC-003: Invalid document type"""
        runner = CliRunner()
        result = runner.invoke(run, ['--topic', 'Valid topic', '--type', 'invalid'])
        assert result.exit_code == 2
        assert 'bizplan' in result.output and 'rd' in result.output

    def test_valid_bizplan_type(self):
        """Test valid bizplan type"""
        runner = CliRunner()
        # Mock orchestrator to avoid actual generation
        result = runner.invoke(run, ['--topic', 'Valid topic', '--type', 'bizplan'])
        # Should not fail on type validation
        assert 'Invalid value for' not in result.output

    def test_valid_rd_type(self):
        """Test valid rd type"""
        runner = CliRunner()
        result = runner.invoke(run, ['--topic', 'Valid topic', '--type', 'rd'])
        # Should not fail on type validation
        assert 'Invalid value for' not in result.output

class TestLanguageValidation:
    def test_invalid_language(self):
        """Test AC-004: Invalid language"""
        runner = CliRunner()
        result = runner.invoke(run, ['--topic', 'Valid topic', '--type', 'bizplan', '--language', 'fr'])
        assert result.exit_code == 2
        assert 'ko' in result.output and 'en' in result.output
```

#### Test Suite: test_run_configuration.py

```python
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from src.cli.run import run

class TestConfigurationValidation:
    @patch('src.cli.run.settings')
    def test_system_not_configured(self, mock_settings):
        """Test AC-005: System not configured"""
        mock_settings.is_configured.return_value = False
        runner = CliRunner()
        result = runner.invoke(run, ['--topic', 'Valid topic', '--type', 'bizplan'])
        assert result.exit_code == 1
        assert 'not configured' in result.output
        assert 'aigenflow setup' in result.output

    @patch('src.cli.run.settings')
    def test_no_valid_sessions(self, mock_settings):
        """Test AC-006: No valid sessions"""
        mock_settings.is_configured.return_value = True
        mock_settings.has_valid_sessions.return_value = False
        mock_settings.has_expired_sessions.return_value = False
        runner = CliRunner()
        result = runner.invoke(run, ['--topic', 'Valid topic', '--type', 'bizplan'])
        assert result.exit_code == 1
        assert 'No valid AI sessions' in result.output

    @patch('src.cli.run.settings')
    def test_expired_sessions(self, mock_settings):
        """Test AC-007: Expired sessions"""
        mock_settings.is_configured.return_value = True
        mock_settings.has_valid_sessions.return_value = False
        mock_settings.has_expired_sessions.return_value = True
        runner = CliRunner()
        result = runner.invoke(run, ['--topic', 'Valid topic', '--type', 'bizplan'])
        assert result.exit_code == 1
        assert 'expired' in result.output
        assert 'aigenflow relogin' in result.output
```

#### Test Suite: test_run_integration.py

```python
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from src.cli.run import run
from pathlib import Path

class TestOrchestratorIntegration:
    @patch('src.cli.run.orchestrator')
    @patch('src.cli.run.settings')
    def test_bizplan_generation(self, mock_settings, mock_orchestrator):
        """Test US-001: Business plan generation"""
        mock_settings.is_configured.return_value = True
        mock_settings.has_valid_sessions.return_value = True

        mock_result = MagicMock()
        mock_result.session_id = "test-session-123"
        mock_result.output_path = Path("./output/test-session-123")
        mock_orchestrator.run_generation.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(run, [
            '--topic', 'AI-powered content generation platform',
            '--type', 'bizplan'
        ])

        assert result.exit_code == 0
        assert 'Generation complete' in result.output
        assert 'test-session-123' in result.output

    @patch('src.cli.run.orchestrator')
    @patch('src.cli.run.settings')
    def test_rd_generation(self, mock_settings, mock_orchestrator):
        """Test US-002: R&D proposal generation"""
        mock_settings.is_configured.return_value = True
        mock_settings.has_valid_sessions.return_value = True

        mock_result = MagicMock()
        mock_result.session_id = "test-session-456"
        mock_result.output_path = Path("./output/test-session-456")
        mock_orchestrator.run_generation.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(run, [
            '--topic', 'Machine learning sentiment analysis',
            '--type', 'rd'
        ])

        assert result.exit_code == 0
        assert 'Generation complete' in result.output
        assert 'test-session-456' in result.output
```

#### Test Suite: test_run_edge_cases.py

```python
import pytest
import signal
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from src.cli.run import run
from pathlib import Path

class TestEdgeCases:
    @patch('src.cli.run.Path.exists')
    @patch('src.cli.run.orchestrator')
    @patch('src.cli.run.settings')
    def test_output_directory_exists(self, mock_settings, mock_orchestrator, mock_exists):
        """Test AC-008: Output directory exists"""
        mock_settings.is_configured.return_value = True
        mock_settings.has_valid_sessions.return_value = True
        mock_exists.return_value = True

        mock_result = MagicMock()
        mock_result.session_id = "existing-session"
        mock_result.output_path = Path("./output/existing-session")
        mock_orchestrator.run_generation.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(run, [
            '--topic', 'Valid topic string',
            '--type', 'bizplan'
        ])

        assert 'Warning: Output directory already exists' in result.output
        assert result.exit_code == 0

    @patch('src.cli.run.orchestrator')
    @patch('src.cli.run.settings')
    def test_pipeline_failure(self, mock_settings, mock_orchestrator):
        """Test AC-009: Pipeline failure"""
        mock_settings.is_configured.return_value = True
        mock_settings.has_valid_sessions.return_value = True
        mock_orchestrator.run_generation.side_effect = Exception("API connection failed")

        runner = CliRunner()
        result = runner.invoke(run, [
            '--topic', 'Valid topic string',
            '--type', 'bizplan'
        ])

        assert result.exit_code == 1
        assert 'Generation failed' in result.output
        assert 'API connection failed' in result.output
```

---

### Integration Tests

#### Test Suite: test_run_e2e.py

```python
import pytest
from click.testing import CliRunner
from src.cli.run import run
from pathlib import Path
import shutil

class TestEndToEnd:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        # Setup: Create test output directory
        self.test_output = Path("./test-output")
        self.test_output.mkdir(exist_ok=True)
        yield
        # Teardown: Clean up test output
        if self.test_output.exists():
            shutil.rmtree(self.test_output)

    @pytest.mark.integration
    def test_full_generation_workflow(self):
        """Test complete generation workflow"""
        runner = CliRunner()

        # This test requires actual configuration
        # Skip if not configured
        result = runner.invoke(run, [
            '--topic', 'AI-powered content generation platform for enterprises',
            '--type', 'bizplan',
            '--language', 'en',
            '--output', str(self.test_output)
        ])

        # If configured, should succeed
        # If not configured, should fail with helpful message
        if result.exit_code != 0:
            assert 'setup' in result.output.lower() or 'configure' in result.output.lower()
```

---

## Quality Gate Criteria

### Tested (TRUST 5 - T)

- [ ] Unit test coverage ≥ 85%
- [ ] All validation tests pass
- [ ] All edge case tests pass
- [ ] Integration tests pass (when configured)
- [ ] No test skips without justification

### Readable (TRUST 5 - R)

- [ ] All functions have docstrings
- [ ] Variable names are descriptive
- [ ] Error messages are clear and actionable
- [ ] Help text is comprehensive
- [ ] Code comments explain complex logic

### Unified (TRUST 5 - U)

- [ ] Follows existing CLI command pattern
- [ ] Uses Click decorators consistently
- [ ] Uses Rich console for all output
- [ ] Error format matches other commands
- [ ] Exit codes are consistent

### Secured (TRUST 5 - S)

- [ ] Input validation for all parameters
- [ ] No command injection vulnerabilities
- [ ] API keys not exposed in logs
- [ ] Safe file path handling
- [ ] Proper error handling without info leakage

### Trackable (TRUST 5 - T)

- [ ] Session IDs are logged
- [ ] Generation status is tracked
- [ ] Errors are logged with context
- [ ] Resume capability is supported
- [ ] Progress is reported

---

## Definition of Done

### Functional Completeness
- [ ] All P0 requirements implemented
- [ ] All acceptance criteria met
- [ ] All edge cases handled
- [ ] Command executes without errors

### Quality Standards
- [ ] Test coverage ≥ 85%
- [ ] Zero linter errors (ruff)
- [ ] Zero type errors (mypy)
- [ ] All TRUST 5 gates passed

### Documentation
- [ ] Code is well-commented
- [ ] Help text is complete
- [ ] README.md updated if needed
- [ ] CHANGELOG.md entry created

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing complete
- [ ] Edge cases verified

### Deployment Readiness
- [ ] Changes are backward compatible
- [ ] No breaking changes
- [ ] Migration guide provided (if needed)
- [ ] Version bump planned

---

## Sign-Off Checklist

### Developer Sign-Off
- [ ] Code implemented according to spec
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated

### QA Sign-Off
- [ ] All acceptance criteria verified
- [ ] Edge cases tested
- [ ] Integration testing complete
- [ ] No regressions found

### Product Sign-Off
- [ ] User stories satisfied
- [ ] User experience acceptable
- [ ] Documentation sufficient
- [ ] Ready for release

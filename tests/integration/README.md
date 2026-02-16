# Integration Tests for SPEC-ENHANCE-003

This directory contains integration and E2E tests for the AigenFlow resilience features, including fault injection testing for the fallback chain mechanism.

## Directory Structure

```
tests/integration/
├── conftest.py              # Shared fixtures and configuration
├── fixtures/                # Test data and mock responses
├── scenarios/               # Test scenario definitions
├── test_fault_injection.py  # E2E fault injection tests
└── README.md                # This file
```

## Test Categories

### 1. Fault Injection Tests

Tests that simulate various failure modes to verify the fallback mechanism:

#### Single Provider Failures
- **Claude timeout -> Gemini fallback**
  - Trigger: Claude request timeout
  - Expected: Automatic fallback to Gemini
  - Verification: Pipeline completes with Gemini response

- **Gemini error -> ChatGPT fallback**
  - Trigger: Gemini returns error response
  - Expected: Fallback to ChatGPT
  - Verification: Error logged, ChatGPT response used

- **Provider rate limit -> next provider**
  - Trigger: Rate limit response (HTTP 429)
  - Expected: Immediate fallback (no retry for rate limits)
  - Verification: Rate limit logged appropriately

#### Cascade Failures
- **All providers timeout -> graceful shutdown**
  - Trigger: All providers timeout
  - Expected: Graceful shutdown with user notification
  - Verification: State saved, error details logged

- **Full chain: Claude -> Gemini -> ChatGPT -> Perplexity**
  - Trigger: Each provider fails sequentially
  - Expected: All transitions logged
  - Verification: Pipeline completes with Perplexity response

#### Network Faults
- **Connection refused -> retry then fallback**
  - Trigger: Network connection refused
  - Expected: 2 retries on same provider, then fallback
  - Verification: Retry count logged

- **DNS failure -> immediate fallback**
  - Trigger: DNS resolution failure
  - Expected: Immediate fallback (no retry for DNS errors)
  - Verification: DNS error logged

#### Partial Failures
- **Phase 1 success, Phase 2 fallback**
  - Trigger: Phase 1 succeeds, Phase 2 primary fails
  - Expected: Phase 1 result preserved, Phase 2 uses fallback
  - Verification: Both phases complete correctly

- **Multiple fallbacks in single phase**
  - Trigger: Claude fails, Gemini fails, ChatGPT succeeds
  - Expected: Phase completes with ChatGPT result
  - Verification: All fallbacks logged

### 2. Circuit Breaker Tests

Tests for the circuit breaker pattern:

- **Circuit opens after threshold**
  - Trigger: 3 consecutive failures
  - Expected: Circuit opens, provider skipped
  - Verification: Requests bypass failed provider

- **Circuit recovery after timeout**
  - Trigger: Circuit opens, timeout expires
  - Expected: Circuit enters half-open state
  - Verification: Test request sent, circuit closes on success

### 3. Provider Selection Tests

Tests for provider selection and routing:

- **Fallback order compliance**
  - Verify: Claude -> Gemini -> ChatGPT -> Perplexity
  - Test: Custom order configuration
  - Test: Context size consideration

## Fixtures

### Fault Injector

```python
def test_with_fault_injection(fault_injector):
    injector = fault_injector
    injector.set_timeout("claude")
    injector.set_error("gemini", 500)

    # Run test...
```

### Mock Provider Factory

```python
def test_with_mock_providers(mock_provider_factory):
    claude = factory.create("claude", success=True, content="Claude response")
    gemini = factory.create("gemini", success=False, error="Timeout")
```

### Pipeline State

```python
def test_pipeline_state(mock_pipeline_state):
    state = mock_pipeline_state
    state.add_fallback_event("claude", "gemini", "timeout")
    assert len(state.fallback_events) == 1
```

## Running Tests

### Run all integration tests
```bash
pytest tests/integration/ -v
```

### Run only fault injection tests
```bash
pytest tests/integration/test_fault_injection.py -v
```

### Run E2E tests only
```bash
pytest tests/integration/test_fault_injection.py -v -m e2e
```

### Run with coverage
```bash
pytest tests/integration/ --cov=src/resilience --cov-report=html
```

## Test Data

### Fixtures Directory

Contains:
- `mock_responses.yaml` - Sample AI responses
- `fault_scenarios.yaml` - Predefined fault scenarios
- `timeout_config.yaml` - Timeout configurations

### Scenarios Directory

Contains:
- `single_failure.json` - Single provider failure scenarios
- `cascade_failures.json` - Multiple provider failure scenarios
- `network_faults.json` - Network-related failure scenarios

## Coverage Targets

- **Overall**: 85%+ code coverage
- **resilience/ module**: 90%+ coverage
- **context/ module**: 90%+ coverage

## Dependencies

These tests are blocked until the following implementations are complete:

- **TASK-005**: FallbackChain 구현
- **TASK-006**: 장애 감지 메커니즘 (Fault detection)
- **TASK-007**: 전환 로그 (Transition logging)

Once these tasks are complete, remove the `@pytest.mark.skip` decorators to enable the tests.

## Contributing

When adding new tests:

1. Define the test scenario in this README
2. Add test data to `fixtures/` if needed
3. Use shared fixtures from `conftest.py`
4. Mark E2E tests with `@pytest.mark.e2e`
5. Update coverage documentation

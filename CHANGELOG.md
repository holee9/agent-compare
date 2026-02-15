# Changelog

All notable changes to the AigenFlow project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CLI utility commands for enhanced user experience
  - `aigenflow check`: Check Playwright browser and AI session status
  - `aigenflow setup`: Interactive setup wizard for first-time configuration
  - `aigenflow relogin [provider]`: Re-authenticate with specific AI provider
  - `aigenflow status [session_id]`: Display pipeline execution status
  - `aigenflow resume <session_id>`: Resume interrupted pipeline execution
  - `aigenflow config show/list/set`: Configuration management
- Phase module separation for improved maintainability
  - `BasePhase` abstract class for all pipeline phases
  - `FramingPhase`, `ResearchPhase`, `StrategyPhase`, `WritingPhase`, `ReviewPhase` as independent modules
- Rich UI components for real-time progress visualization
  - `PipelineProgress`: Progress bars for pipeline execution
  - `LogStream`: Rich panel for real-time log streaming
  - `PhaseSummary`: Rich table for phase completion summary
- Comprehensive test suite with 135 tests (85%+ coverage)

### Changed
- Refactored `orchestrator.py` to use Phase classes while maintaining 100% backward compatibility
- Updated `main.py` to integrate all CLI commands with Typer app
- Fixed import inconsistency in `gateway/base.py`

### Fixed
- Session manager status checking
- Phase module dependencies and imports

## [2.0.0] - 2026-02-15

### Added
- Multi-AI pipeline orchestration with 5 phases
- Playwright-based AI gateway with 4 providers (ChatGPT, Claude, Gemini, Perplexity)
- 12 Jinja2 prompt templates for all pipeline phases
- Session management with 4-stage auto-recovery chain
- Pipeline state persistence and resume functionality
- Template manager with multiple output formats

### Changed
- Migrated from agent-compare to aigenflow project structure

[Unreleased]: https://github.com/yourusername/aigenflow/compare/v2.0.0...HEAD
[v2.0.0]: https://github.com/yourusername/aigenflow/releases/tag/v2.0.0

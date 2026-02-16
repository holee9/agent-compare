# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- PyPI packaging configuration with proper entry points
- GitHub Actions CI/CD workflows for testing and releases
- Standalone launcher script (aigenflow.py)
- Lazy loading support in aigenflow package imports

### Fixed
- Pydantic field_validator decorators - changed from instance methods to class methods
- All lint errors (33 → 0)
- Template unit tests now passing (12/12)
- Logging profile unit tests now passing (45/45)
- Import path issues in CLI entry points

### Changed
- Python version requirement: >=3.11 (down from >=3.13 for compatibility)
- Ruff target version: py311 (down from py313)
- All module imports now use proper path handling for editable installs

## [0.1.0] - 2026-02-16

### Added
- Initial release of AigenFlow
- Multi-AI pipeline CLI tool for automated business plan generation
- Support for Claude, ChatGPT, Gemini, and Perplexity AI providers
- Template-based prompt system with 12 phase-specific templates
- Rich UI components for progress tracking and logging
- Structured logging with environment profiles (development, testing, production)
- Token counting and context summarization
- Cache management for AI responses
- Configuration management with Pydantic settings

[Unreleased]: https://github.com/holee9/aigenflow/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/holee9/aigenflow/releases/tag/v0.1.0

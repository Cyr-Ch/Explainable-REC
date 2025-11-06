# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- LLM support with ICL examples for CoderAgent and InterpreterAgent
- Debug logging capability (`--debug` flag)
- Rule-based fallback when LLM is unavailable
- ICL examples for interpreter (`chatsgp/icl/interpreter_examples.jsonl`)
- Automatic `.env` file loading
- Enhanced human-readable interpretations
- `.gitignore` file
- Package installation via `setup.py`

### Changed
- CoderAgent now uses LLM with ICL examples (with rule-based fallback)
- InterpreterAgent now uses LLM with ICL examples (with rule-based fallback)
- Output format now includes detailed human-readable answers
- Currency display changed from € to EUR for better compatibility

### Fixed
- JSON encoding for Unicode characters (Euro symbol)
- Module import issues (added `__init__.py` files)
- Environment variable loading from `.env` file

## [0.1.0] - 2024-01-XX

### Added
- Initial release
- Multi-agent pipeline (Coder → Optimizer → Interpreter)
- Support for PuLP and Gurobi solvers
- AutoGen orchestration option
- Dataset builder
- Basic rule-based question parsing


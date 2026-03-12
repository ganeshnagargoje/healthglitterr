# Installation Guide

## Development Setup

To set up the project for development, install it in editable mode:

```bash
# Navigate to the project directory
cd agentic-medical-health-review

# Install in editable mode (development mode)
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## What This Does

Installing with `-e` (editable mode) allows you to:
- Import modules from anywhere in the project without sys.path hacks
- Make changes to the code without reinstalling
- Run tests and scripts with proper imports

## Verify Installation

After installation, you should be able to import from anywhere:

```python
from models.normalized_parameter import NormalizedParameter
from tools.src.analysis_computation_tools.mismatch_detection import detect_mismatch
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/tools/analysis_computation_tools/test_mismatch_detection_tool.py
```

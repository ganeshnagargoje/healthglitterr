# Testing Guide - Medical Health Review System

This guide explains how to run tests in the Docker environment.

## Quick Start

### Using PowerShell Script (Windows)
```powershell
# Run all tests
.\run-tests.ps1

# Run specific test suites
.\run-tests.ps1 normalize
.\run-tests.ps1 parser
.\run-tests.ps1 e2e
.\run-tests.ps1 quick
```

### Using Makefile (Linux/Mac/Windows with Make)
```bash
# Run all tests
make test

# Run specific tests
make test-normalize
make test-parser
make test-e2e
```

### Using Docker Compose Directly
```bash
# Run all tests
docker-compose exec -T app bash -c "cd agentic-medical-health-review && python -m pytest tests/ -v"

# Run specific test file
docker-compose exec -T app bash -c "cd agentic-medical-health-review && python -m pytest tests/tools/document_data_extraction_tools/test_normalize_lab_data.py -v"

# Run with specific markers
docker-compose exec -T app bash -c "cd agentic-medical-health-review && python -m pytest tests/ -v -m integration"
```

## Test Structure

```
agentic-medical-health-review/tests/
├── tools/
│   ├── document_data_extraction_tools/
│   │   ├── test_normalize_lab_data.py      # Lab data normalization tests
│   │   ├── test_normalize_with_real_data.py # Real database tests
│   │   ├── test_end_to_end_integration.py   # E2E workflow tests
│   │   ├── test_real_file.py                # PDF parser tests
│   │   └── conftest.py                      # Pytest fixtures
│   └── intake_validation_tools/
│       └── test_validate_input.py           # Input validation tests
└── test_data/
    └── sample_reports/                      # Sample PDF files
```

## Test Results

Current test status: **55/55 tests passing (100%)**

### Test Breakdown
- Document Data Extraction: 17 tests
- Intake Validation: 38 tests

## Fixes Applied

### 1. Import Path Issues
**Problem**: Tests couldn't import modules due to incorrect Python paths.

**Solution**: 
- Updated test files to use correct import paths with `pathlib`
- Added proper `sys.path` configuration in test files
- Updated `Dockerfile` to set `PYTHONPATH=/app:/app/agentic-medical-health-review`

### 2. Database Foreign Key Constraints
**Problem**: Tests were creating parameter_ids that didn't exist in the database, causing foreign key violations.

**Solution**:
- Created pytest fixtures (`test_user_id`, `create_health_parameter`) that properly set up test data
- Tests now create actual database records before testing normalization
- Added proper cleanup in fixture teardown

### 3. Database Schema Mismatch
**Problem**: Cleanup code used wrong column name (`parameter_id` instead of `original_parameter_id`).

**Solution**:
- Fixed cleanup queries to use correct column name: `original_parameter_id`
- Ensured proper deletion order to respect foreign key constraints

### 4. Test Configuration
**Problem**: No centralized pytest configuration.

**Solution**:
- Created `pytest.ini` with proper test discovery and output settings
- Added test markers for organizing tests (unit, integration, e2e, slow, database)

## Pytest Configuration

The `pytest.ini` file includes:
- Test discovery patterns
- Output formatting options
- Test markers for categorization
- Path configuration

## Test Markers

Use markers to run specific test categories:

```bash
# Run only unit tests
docker-compose exec -T app bash -c "cd agentic-medical-health-review && python -m pytest tests/ -v -m unit"

# Run only integration tests
docker-compose exec -T app bash -c "cd agentic-medical-health-review && python -m pytest tests/ -v -m integration"

# Run only database tests
docker-compose exec -T app bash -c "cd agentic-medical-health-review && python -m pytest tests/ -v -m database"

# Skip slow tests
docker-compose exec -T app bash -c "cd agentic-medical-health-review && python -m pytest tests/ -v -m 'not slow'"
```

## Troubleshooting

### Tests fail with "ModuleNotFoundError"
**Solution**: Ensure you're running tests from within the `agentic-medical-health-review` directory:
```bash
docker-compose exec -T app bash -c "cd agentic-medical-health-review && python -m pytest tests/ -v"
```

### Tests fail with "Database connection error"
**Solution**: Ensure the database container is healthy:
```bash
docker-compose ps
docker-compose logs postgres
```

### Tests fail with "Foreign key constraint violation"
**Solution**: The test fixtures should handle this automatically. If issues persist, check that the database schema is up to date:
```bash
make db-init
```

### Container not running
**Solution**: Start the containers:
```bash
docker-compose up -d
# Wait for services to be ready
sleep 15
```

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Start services
docker-compose up -d

# Wait for services to be ready
sleep 15

# Run tests with JUnit XML output
docker-compose exec -T app bash -c "cd agentic-medical-health-review && python -m pytest tests/ -v --junitxml=test-results.xml"

# Stop services
docker-compose down
```

## Adding New Tests

When adding new tests:

1. Follow the existing test structure
2. Use pytest fixtures for database setup/teardown
3. Add appropriate test markers
4. Ensure tests clean up after themselves
5. Test both success and failure cases

Example test template:

```python
import pytest
from models.database_connection import DatabaseConnection

@pytest.mark.unit
def test_my_feature(test_user_id, create_health_parameter):
    """Test description"""
    # Arrange
    param_id = create_health_parameter("Test Param", 100.0, "mg/dL")
    
    # Act
    result = my_function(param_id)
    
    # Assert
    assert result['success'] == True
    # Cleanup is automatic via fixture
```

## Performance

Test execution times:
- Full test suite: ~40-45 seconds
- Unit tests only: ~5-10 seconds
- Integration tests: ~30-35 seconds

## Next Steps

To improve the test suite:
1. Add more edge case tests
2. Implement property-based testing with Hypothesis
3. Add performance benchmarks
4. Increase code coverage
5. Add mutation testing

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test output for specific error messages
3. Check Docker logs: `docker-compose logs app`
4. Verify database connectivity: `make status`

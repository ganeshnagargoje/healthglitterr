@echo off
REM Run health input validation tests with JSON report generation
REM Usage: run_health_tests.bat

python -m pytest agentic-medical-health-review\tests\tools\intake_validation_tools\test_validate_input.py -v --json-report --json-report-file=agentic-medical-health-review\tests\tools\intake_validation_tools\test_report.json

echo.
echo JSON Report saved to: agentic-medical-health-review\tests\tools\intake_validation_tools\test_report.json

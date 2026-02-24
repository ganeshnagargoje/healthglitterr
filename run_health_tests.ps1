# Run health input validation tests with JSON report generation
# Usage: .\run_health_tests.ps1

param(
    [switch]$NoReport,  # Skip JSON report generation
    [string]$Filter     # Run specific tests (e.g., -Filter "TestValidateHealthInputBasic")
)

$testFile = "agentic-medical-health-review\tests\tools\intake_validation_tools\test_validate_input.py"
$reportFile = "agentic-medical-health-review\tests\tools\intake_validation_tools\test_report.json"

# Build pytest command
$cmd = "python -m pytest $testFile -v"

# Add filter if provided
if ($Filter) {
    $cmd += " -k $Filter"
}

# Add JSON report if not skipped
if (-not $NoReport) {
    $cmd += " --json-report --json-report-file=$reportFile"
}

Write-Host "Running: $cmd" -ForegroundColor Cyan
Invoke-Expression $cmd

if (-not $NoReport) {
    Write-Host "`nJSON Report saved to: $reportFile" -ForegroundColor Green
}

# PowerShell script to run tests in Docker
# Usage: .\run-tests.ps1 [test-type]
# test-type: all (default), normalize, parser, e2e

param(
    [string]$TestType = "all"
)

Write-Host "🐳 Medical Health Review System - Test Runner" -ForegroundColor Cyan
Write-Host "=" * 60

# Check if Docker is running
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if containers are running
$appRunning = docker-compose ps -q app
if (-not $appRunning) {
    Write-Host "⚠️  Containers are not running. Starting them..." -ForegroundColor Yellow
    docker-compose up -d
    Start-Sleep -Seconds 15
}

Write-Host ""

switch ($TestType) {
    "all" {
        Write-Host "🧪 Running all tests..." -ForegroundColor Green
        docker-compose exec -T app bash -c "cd agentic-medical-health-review && python -m pytest tests/ -v"
    }
    "normalize" {
        Write-Host "🧪 Running normalize lab data tests..." -ForegroundColor Green
        docker-compose exec -T app bash -c "cd agentic-medical-health-review && python -m pytest tests/tools/document_data_extraction_tools/test_normalize_lab_data.py -v"
    }
    "parser" {
        Write-Host "🧪 Running lab report parser tests..." -ForegroundColor Green
        docker-compose exec -T app bash -c "cd agentic-medical-health-review && python tests/tools/document_data_extraction_tools/test_real_file.py tests/test_data/sample_reports/lab_report1_page_1.pdf --format text"
    }
    "e2e" {
        Write-Host "🧪 Running end-to-end integration test..." -ForegroundColor Green
        docker-compose exec -T app bash -c "cd agentic-medical-health-review && python tests/tools/document_data_extraction_tools/test_end_to_end_integration.py tests/test_data/sample_reports/lab_report1_page_1.pdf"
    }
    "quick" {
        Write-Host "🧪 Running quick test suite..." -ForegroundColor Green
        docker-compose exec -T app bash -c "cd agentic-medical-health-review && python -m pytest tests/ -v -m 'not slow'"
    }
    default {
        Write-Host "❌ Unknown test type: $TestType" -ForegroundColor Red
        Write-Host "Valid options: all, normalize, parser, e2e, quick" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "✅ Test execution complete!" -ForegroundColor Green

# PowerShell Setup Script for Medical Health Review System
# For Windows users

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Medical Health Review System - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Copy .env file if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host "⚠  Please edit .env file with your configuration if needed" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Write-Host ""

# Build and start containers
Write-Host "Building Docker containers..." -ForegroundColor Yellow
Write-Host "(This may take 5-10 minutes on first run)" -ForegroundColor Gray
Write-Host "(Using binary wheels when available)" -ForegroundColor Gray
docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Build complete" -ForegroundColor Green
Write-Host ""

# Start services
Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to start services!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Services started" -ForegroundColor Green
Write-Host ""

# Wait for database to be ready
Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check database connection
Write-Host "Testing database connection..." -ForegroundColor Yellow
docker-compose exec -T app python -c "from models.database_connection import DatabaseConnection; with DatabaseConnection() as db: print('Database connection successful!')"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database connection successful" -ForegroundColor Green
} else {
    Write-Host "⚠  Database connection failed - it may need more time to initialize" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services running:" -ForegroundColor White
Write-Host "  • Application:  http://localhost:8000" -ForegroundColor Gray
Write-Host "  • Database:     localhost:5432" -ForegroundColor Gray
Write-Host "  • pgAdmin:      http://localhost:5050 (optional)" -ForegroundColor Gray
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor White
Write-Host "  • View logs:        docker-compose logs -f" -ForegroundColor Gray
Write-Host "  • Stop services:    docker-compose down" -ForegroundColor Gray
Write-Host "  • Restart services: docker-compose restart" -ForegroundColor Gray
Write-Host "  • Run tests:        docker-compose exec app python -m pytest tests/" -ForegroundColor Gray
Write-Host ""
Write-Host "For more commands, see DOCKER_SETUP_GUIDE.md" -ForegroundColor Yellow
Write-Host ""

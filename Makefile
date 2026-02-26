# Makefile for Medical Health Review System
# Simplifies Docker commands for developers

.PHONY: help setup start stop restart logs shell db-shell test clean rebuild

# Default target
help:
	@echo "Medical Health Review System - Docker Commands"
	@echo ""
	@echo "Setup & Start:"
	@echo "  make setup          - Initial setup (copy .env, build, start)"
	@echo "  make start          - Start all services"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo ""
	@echo "Development:"
	@echo "  make logs           - View logs (all services)"
	@echo "  make logs-app       - View application logs"
	@echo "  make logs-db        - View database logs"
	@echo "  make shell          - Access application shell"
	@echo "  make db-shell       - Access database shell"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-normalize - Test normalize lab data"
	@echo "  make test-parser    - Test lab report parser"
	@echo "  make test-e2e       - Run end-to-end integration test"
	@echo ""
	@echo "Database:"
	@echo "  make db-init        - Initialize database tables"
	@echo "  make db-backup      - Backup database"
	@echo "  make db-restore     - Restore database from backup"
	@echo ""
	@echo "Maintenance:"
	@echo "  make rebuild        - Rebuild containers (after dependency changes)"
	@echo "  make clean          - Stop and remove all containers/volumes"
	@echo "  make status         - Show container status"
	@echo ""

# Setup - First time only
setup:
	@echo "🚀 Setting up Medical Health Review System..."
	@if [ ! -f .env ]; then \
		echo "📝 Copying .env.example to .env..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env file with your configuration"; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@echo "🔨 Building Docker containers..."
	docker-compose build
	@echo "🚀 Starting services..."
	docker-compose up -d
	@echo "⏳ Waiting for database to be ready..."
	@sleep 10
	@echo "✅ Setup complete! Run 'make status' to check services"

# Start services
start:
	@echo "🚀 Starting services..."
	docker-compose up -d
	@echo "✅ Services started"

# Stop services
stop:
	@echo "🛑 Stopping services..."
	docker-compose down
	@echo "✅ Services stopped"

# Restart services
restart:
	@echo "🔄 Restarting services..."
	docker-compose restart
	@echo "✅ Services restarted"

# View logs
logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f app

logs-db:
	docker-compose logs -f postgres

# Access shells
shell:
	@echo "🐚 Accessing application shell..."
	docker-compose exec app bash

db-shell:
	@echo "🐚 Accessing database shell..."
	docker-compose exec postgres psql -U postgres -d medical_health_review

# Run tests
test:
	@echo "🧪 Running all tests..."
	docker-compose exec app bash -c "cd agentic-medical-health-review && python -m pytest tests/ -v"

test-normalize:
	@echo "🧪 Testing normalize lab data..."
	docker-compose exec app bash -c "cd agentic-medical-health-review && python tests/tools/document_data_extraction_tools/test_normalize_with_real_data.py"

test-parser:
	@echo "🧪 Testing lab report parser..."
	docker-compose exec app bash -c "cd agentic-medical-health-review && python tests/tools/document_data_extraction_tools/test_real_file.py tests/test_data/sample_reports/lab_report1_page_1.pdf --format text"

test-e2e:
	@echo "🧪 Running end-to-end integration test..."
	docker-compose exec app bash -c "cd agentic-medical-health-review && python tests/tools/document_data_extraction_tools/test_end_to_end_integration.py tests/test_data/sample_reports/lab_report1_page_1.pdf"

# Database operations
db-init:
	@echo "🗄️  Initializing database tables..."
	docker-compose exec postgres psql -U postgres -d medical_health_review -f /docker-entrypoint-initdb.d/01-init-schema.sql
	docker-compose exec postgres psql -U postgres -d medical_health_review -f /docker-entrypoint-initdb.d/02-normalization-tables.sql
	docker-compose exec postgres psql -U postgres -d medical_health_review -f /docker-entrypoint-initdb.d/03-additional-parameter-mappings.sql
	@echo "✅ Database initialized"

db-backup:
	@echo "💾 Backing up database..."
	docker-compose exec postgres pg_dump -U postgres medical_health_review > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Database backed up"

db-restore:
	@echo "📥 Restoring database from backup.sql..."
	@if [ -f backup.sql ]; then \
		docker-compose exec -T postgres psql -U postgres medical_health_review < backup.sql; \
		echo "✅ Database restored"; \
	else \
		echo "❌ backup.sql not found"; \
	fi

# Rebuild containers
rebuild:
	@echo "🔨 Rebuilding containers..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "✅ Containers rebuilt"

# Clean everything
clean:
	@echo "🧹 Cleaning up..."
	@echo "⚠️  This will remove all containers and volumes!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "✅ Cleanup complete"; \
	else \
		echo "❌ Cleanup cancelled"; \
	fi

# Show status
status:
	@echo "📊 Container Status:"
	@docker-compose ps
	@echo ""
	@echo "🔍 Health Check:"
	@docker-compose exec app python -c "from models.database_connection import DatabaseConnection; with DatabaseConnection() as db: print('✅ Database connection: OK')" 2>/dev/null || echo "❌ Database connection: FAILED"

# Medical Health Review System

> **🚀 5-minute setup with Docker - Zero dependencies required!**

## Table of Contents
- [Quick Start](#-quick-start)
- [Team](#-team)
- [Project Overview](#-project-overview)
- [Project Structure](#-project-structure)
- [Tools Implemented](#️-tools-implemented)
- [Docker Setup](#-docker-setup)
- [Testing](#-testing)
- [Database](#-database)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

```bash
# 1. Install Docker Desktop (only requirement!)
# Download from: https://www.docker.com/products/docker-desktop/

# 2. Clone and setup
git clone <repository-url>
cd healthglitterr

# 3. Run setup script
# Windows:
.\setup.ps1

# Linux/Mac:
chmod +x setup.sh
./setup.sh

# Done! Everything is running ✅
```

---

## 👥 Team

**Members**: 
1. Sanchit Mehara 
2. Ganesh Nagargoje 
3. Satheeshkumar Rajasekaran 
4. Pradeep CR   
5. Amulya Kumar     

**Room No: 9 — Medical Report Trend + Holistic Health Review (Multi-Agent)** 

---

## 🎯 Project Overview

**Problem Context** 

People receive lab/medical reports as PDFs with many parameters over time. Manually tracking trends (diabetes, liver, kidney, thyroid, etc.) is difficult; patients miss early warnings. Reports are reviewed episodically, not longitudinally. Lack of personalized, multi-language interpretation creates confusion and delayed action. 

**Primary Goal** 

The agent's goal is to analyze reports, detect trends, and produce holistic guidance, subject to medical safety constraints + report validity + user consent, while optimizing for early risk detection and understandable summaries. 

**Scope and Boundaries** 

Allowed: extract parameters, trend charts, risk flags, medication interaction reminders (non-prescriptive), lifestyle suggestions, regional language summary. 

Stop/ask human: high-risk findings, medication changes, diagnosis. 

Out of scope: prescribing/altering treatment. 

**User Types** 

Patient, Caregiver, Doctor (review), Lab admin. 

**Conversation Examples** 

User uploads reports → Agent: "HbA1c rising 3 cycles—risk flag; book doctor?" 

User: "Explain in Hindi/Tamil." → Agent provides translated summary + next-step checklist. 

---

## 📁 Project Structure

```
healthglitterr/
├── START_HERE.md                    ⭐ Start here for setup
├── docker-compose.yml               Docker orchestration
├── Dockerfile                       Application container
├── setup.sh / setup.ps1             Setup scripts
├── Makefile                         Command shortcuts (Linux/Mac)
│
├── agentic-medical-health-review/   Main application
│   ├── docs/                        Documentation
│   │   ├── agent_states.md
│   │   ├── agent_io_contract.md
│   │   └── state_diagram.mmd
│   │
│   ├── tools/                       Tool implementations
│   │   ├── src/
│   │   │   ├── document_data_extraction_tools/
│   │   │   │   ├── lab_report_parser/
│   │   │   │   └── normalize_lab_data/
│   │   │   └── intake_validation_tools/
│   │   └── specs/                   Tool specifications
│   │
│   ├── prompts/                     Agent prompts
│   │   ├── system_prompt.md
│   │   └── safety_policy.md
│   │
│   └── models/                      Data models
│       ├── database_connection.py
│       ├── lab_parameter.py
│       └── normalized_parameter.py
│
├── tests/                           Test files
│   ├── tools/
│   │   └── document_data_extraction_tools/
│   │       ├── test_normalize_with_real_data.py
│   │       ├── test_end_to_end_integration.py
│   │       └── test_real_file.py
│   └── test_data/
│       └── sample_reports/
│
└── init-scripts/                    Database initialization
    ├── 01-init-schema.sql
    ├── 02-normalization-tables.sql
    └── 03-additional-parameter-mappings.sql
```

## 🧪 Testing

### Current Status
**55/55 tests passing (100%)**
- Document Data Extraction: 17 tests
- Intake Validation: 38 tests

### Quick Test Commands

```bash
# All tests
docker-compose exec app python -m pytest tests/ -v

# Specific test suites
docker-compose exec app python -m pytest tests/tools/document_data_extraction_tools/ -v

# Using PowerShell script (Windows)
.\run-tests.ps1

# Using Makefile (Linux/Mac)
make test
```

### Test Structure
```
agentic-medical-health-review/tests/
├── tools/
│   ├── document_data_extraction_tools/
│   │   ├── test_normalize_lab_data.py
│   │   ├── test_normalize_with_real_data.py
│   │   ├── test_end_to_end_integration.py
│   │   └── test_real_file.py
│   └── intake_validation_tools/
│       └── test_validate_input.py
└── test_data/
    └── sample_reports/
```

### Test Markers

Run specific test categories:

```bash
# Unit tests only
docker-compose exec app python -m pytest tests/ -v -m unit

# Integration tests only
docker-compose exec app python -m pytest tests/ -v -m integration

# Database tests only
docker-compose exec app python -m pytest tests/ -v -m database

# Skip slow tests
docker-compose exec app python -m pytest tests/ -v -m 'not slow'
```

### Adding New Tests

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

---

## 📊 Database

### PostgreSQL 16 Setup

**Services:**
- PostgreSQL 16 - Main database
- pgAdmin (optional) - Database UI at http://localhost:5050

**Connection Details:**
- Host: localhost
- Port: 5432
- Database: medical_health_review
- User: postgres
- Password: postgres (change in .env)
- Connection String: `postgresql://postgres:postgres@localhost:5432/medical_health_review`

### Quick Access

```bash
# Via Docker
docker-compose exec postgres psql -U postgres -d medical_health_review

# Via host (when running)
psql -h localhost -U postgres -d medical_health_review
```

### Database Tables

- `users` - User accounts
- `medical_reports` - Uploaded reports
- `health_parameters` - Raw lab data
- `normalized_parameters` - Standardized lab data
- `normalization_audit_logs` - Audit trail
- `parameter_name_mappings` - Name standardization rules
- `unit_conversion_rules` - Unit conversion factors
- `standard_reference_ranges` - Reference ranges

### Backup & Restore

```bash
# Backup
docker-compose exec postgres pg_dump -U postgres medical_health_review > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres medical_health_review < backup.sql
```

### pgAdmin (Optional)

```bash
# Start pgAdmin
docker-compose --profile admin up -d

# Access at http://localhost:5050
# Email: admin@example.com
# Password: admin
```

---

## 🔧 Development

### Daily Workflow

```bash
# 1. Start services
docker-compose up -d

# 2. Make code changes (automatically reflected in container)

# 3. Run tests
docker-compose exec app python -m pytest tests/

# 4. View logs
docker-compose logs -f app

# 5. Stop when done
docker-compose down
```

### Common Commands

#### Using Makefile (Linux/Mac)
```bash
make start          # Start all services
make stop           # Stop all services
make test           # Run all tests
make logs           # View logs
make shell          # Access application shell
make db-shell       # Access database shell
make rebuild        # Rebuild containers
make help           # Show all commands
```

#### Using Docker Compose (All Platforms)
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Access shell
docker-compose exec app bash

# Rebuild after dependency changes
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🚀 Production Deployment

### Build Production Image
```bash
docker build -t medical-health-review:1.0.0 .
```

### Push to Registry
```bash
docker tag medical-health-review:1.0.0 your-registry/medical-health-review:1.0.0
docker push your-registry/medical-health-review:1.0.0
```

### Production Checklist
- Remove volume mounts for source code
- Use production environment variables
- Implement proper secrets management
- Add health checks and monitoring
- Configure logging and alerting

---


# Medical Health Review System

> **🚀 NEW DEVELOPERS: Start with [START_HERE.md](START_HERE.md) for 5-minute setup!**

---

## 📋 Quick Links for Developers

- **[START_HERE.md](START_HERE.md)** ⭐ - **New developer setup (5 minutes)**
- [README_DOCKER.md](README_DOCKER.md) - Docker quick reference
- [DOCKER_SETUP_GUIDE.md](DOCKER_SETUP_GUIDE.md) - Comprehensive Docker guide
- [DOCKER_SOLUTION_SUMMARY.md](DOCKER_SOLUTION_SUMMARY.md) - Why Docker solves dependency issues
- [WINDOWS_SETUP.md](WINDOWS_SETUP.md) - Windows-specific setup instructions
- [PIP_BINARY_WHEELS_SOLUTION.md](PIP_BINARY_WHEELS_SOLUTION.md) - Binary wheels configuration

---

## 🚀 Quick Start

### For New Developers:
```bash
# 1. Install Docker Desktop (only requirement!)
# Download from: https://www.docker.com/products/docker-desktop/

# 2. Clone repository
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

### For Existing Developers:
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Run tests
docker-compose exec app python -m pytest tests/
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

---

## 🛠️ Tools Implemented

### 1. Lab Report Parser
- **Location:** `tools/src/document_data_extraction_tools/lab_report_parser/`
- **Purpose:** Extract lab data from PDF/image reports using OCR
- **Features:**
  - PDF to image conversion
  - PaddleOCR text extraction
  - LLM-based structured data extraction
  - Supports multiple file formats

### 2. Normalize Lab Data
- **Location:** `tools/src/document_data_extraction_tools/normalize_lab_data/`
- **Purpose:** Standardize extracted lab parameters
- **Features:**
  - Parameter name standardization
  - Unit conversion
  - Reference range alignment
  - Confidence scoring
  - Audit trail logging

### 3. End-to-End Integration
- **Test:** `tests/tools/document_data_extraction_tools/test_end_to_end_integration.py`
- **Workflow:** PDF → Extract → Normalize → Database
- **Result:** 100% success rate on sample data

---

## 🧪 Running Tests

```bash
# All tests
docker-compose exec app python -m pytest tests/ -v

# Specific tests
docker-compose exec app python tests/tools/document_data_extraction_tools/test_normalize_with_real_data.py
docker-compose exec app python tests/tools/document_data_extraction_tools/test_real_file.py tests/test_data/sample_reports/lab_report1_page_1.pdf
docker-compose exec app python tests/tools/document_data_extraction_tools/test_end_to_end_integration.py tests/test_data/sample_reports/lab_report1_page_1.pdf
```

---

## 📊 Database

### Services:
- **PostgreSQL 16** - Main database
- **pgAdmin** (optional) - Database UI at http://localhost:5050

### Tables:
- `users` - User accounts
- `medical_reports` - Uploaded reports
- `health_parameters` - Raw lab data
- `normalized_parameters` - Standardized lab data
- `normalization_audit_logs` - Audit trail
- `parameter_name_mappings` - Name standardization rules
- `unit_conversion_rules` - Unit conversion factors
- `standard_reference_ranges` - Reference ranges

### Access:
```bash
# Via Docker
docker-compose exec postgres psql -U postgres -d medical_health_review

# Via host (when running)
psql -h localhost -U postgres -d medical_health_review
```

---

## 🔧 Development

### Daily Workflow:
```bash
# 1. Start services
docker-compose up -d

# 2. Make code changes (on your machine)
# Changes automatically reflected in container

# 3. Run tests
docker-compose exec app python -m pytest tests/

# 4. View logs
docker-compose logs -f app

# 5. Stop when done
docker-compose down
```

### After Dependency Changes:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---


## 📝 License

[Add your license here]

---


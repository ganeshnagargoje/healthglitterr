# 🐳 Docker Setup - Zero Dependency Installation

## Why Docker?

Docker solves the **"it works on my machine"** problem by ensuring:
- ✅ **Identical environments** for all developers
- ✅ **Zero manual dependency installation**
- ✅ **No version conflicts**
- ✅ **One-command setup**
- ✅ **Works on Windows, Mac, and Linux**

---

## 🚀 Quick Start (3 Steps)

### 1. Install Docker Desktop
Download and install from: https://www.docker.com/products/docker-desktop/

### 2. Clone & Setup
```bash
# Clone repository
git clone <repository-url>
cd healthglitterr

# Run setup script
# Windows (PowerShell):
.\setup.ps1

# Linux/Mac:
chmod +x setup.sh
./setup.sh
```

### 3. Done! 🎉
Everything is now running:
- PostgreSQL database with all tables
- Python application with all dependencies
- All tools ready to use

---

## 📦 What Gets Installed Automatically

### System Dependencies:
- Python 3.12
- PostgreSQL 16
- poppler-utils (PDF processing)
- OpenCV libraries (image processing)
- PaddleOCR (OCR engine)
- All required system libraries

### Python Packages (from requirements.txt):
- psycopg2-binary (PostgreSQL adapter)
- pydantic (data validation)
- paddleocr (OCR)
- pdf2image (PDF processing)
- openai (LLM integration)
- pytest (testing)
- And 30+ other dependencies

### Database:
- All tables created automatically
- Sample data loaded
- Ready for use

---

## 🎯 Common Commands

### Using Makefile (Recommended - Linux/Mac):
```bash
make start          # Start all services
make stop           # Stop all services
make test           # Run all tests
make logs           # View logs
make shell          # Access application shell
make db-shell       # Access database shell
make help           # Show all commands
```

### Using Docker Compose (All Platforms):
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Run tests
docker-compose exec app python -m pytest tests/

# Access shell
docker-compose exec app bash

# Access database
docker-compose exec postgres psql -U postgres -d medical_health_review
```

---

## 🧪 Running Tests

### All Tests:
```bash
docker-compose exec app python -m pytest tests/ -v
```

### Specific Tests:
```bash
# Normalize lab data
docker-compose exec app python tests/tools/document_data_extraction_tools/test_normalize_with_real_data.py

# Lab report parser
docker-compose exec app python tests/tools/document_data_extraction_tools/test_real_file.py tests/test_data/sample_reports/lab_report1_page_1.pdf

# End-to-end integration
docker-compose exec app python tests/tools/document_data_extraction_tools/test_end_to_end_integration.py tests/test_data/sample_reports/lab_report1_page_1.pdf
```

---

## 🔧 Development Workflow

### 1. Start Development:
```bash
docker-compose up -d
```

### 2. Make Code Changes:
- Edit files on your machine
- Changes are automatically reflected in container

### 3. Run Tests:
```bash
docker-compose exec app python -m pytest tests/
```

### 4. View Logs:
```bash
docker-compose logs -f app
```

### 5. Stop When Done:
```bash
docker-compose down
```

---

## 🐛 Troubleshooting

### "Cannot connect to Docker daemon"
**Solution:** Start Docker Desktop

### "Port already in use"
**Solution:** Edit `.env` file and change ports:
```env
POSTGRES_PORT=5433
APP_PORT=8001
```

### "Database connection failed"
**Solution:** Wait for database to initialize:
```bash
docker-compose ps  # Check status
# Wait until postgres shows "healthy"
```

### "Module not found"
**Solution:** Rebuild containers:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### "Out of disk space"
**Solution:** Clean up Docker:
```bash
docker system prune -a --volumes
```

---

## 📊 Accessing Services

### Application
- **URL:** http://localhost:8000
- **Container:** medical-health-review-app

### PostgreSQL Database
- **Host:** localhost
- **Port:** 5432
- **Database:** medical_health_review
- **User:** postgres
- **Password:** postgres (change in .env)
- **Connection String:** `postgresql://postgres:postgres@localhost:5432/medical_health_review`

### pgAdmin (Optional)
- **URL:** http://localhost:5050
- **Email:** admin@example.com
- **Password:** admin
- **Start:** `docker-compose --profile admin up -d`

---

## 🔄 Updating Dependencies

### After changing requirements.txt:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Or using Makefile:
```bash
make rebuild
```

---

## 💾 Data Persistence

Data is stored in Docker volumes and persists across container restarts:
- `postgres_data` - Database files
- `app_data` - Application data
- `patient_data` - Patient records

### Backup Database:
```bash
docker-compose exec postgres pg_dump -U postgres medical_health_review > backup.sql
```

### Restore Database:
```bash
docker-compose exec -T postgres psql -U postgres medical_health_review < backup.sql
```

---

## 🚀 Production Deployment

### Build Production Image:
```bash
docker build -t medical-health-review:1.0.0 .
```

### Push to Registry:
```bash
docker tag medical-health-review:1.0.0 your-registry/medical-health-review:1.0.0
docker push your-registry/medical-health-review:1.0.0
```

### Deploy:
Use the production docker-compose.yml with:
- Removed volume mounts for source code
- Production environment variables
- Proper secrets management
- Health checks and monitoring

---

## 📚 Additional Documentation

- **Detailed Guide:** See `DOCKER_SETUP_GUIDE.md`
- **Docker Docs:** https://docs.docker.com/
- **Docker Compose Docs:** https://docs.docker.com/compose/

---

## ✅ Verification

After setup, verify everything works:

```bash
# 1. Check containers
docker-compose ps

# 2. Test database
docker-compose exec app python -c "from models.database_connection import DatabaseConnection; with DatabaseConnection() as db: print('✅ Database OK')"

# 3. Run a test
docker-compose exec app python tests/tools/document_data_extraction_tools/test_normalize_with_real_data.py
```

If all pass: **✅ Setup Complete!**

---

## 🆘 Need Help?

1. Check `DOCKER_SETUP_GUIDE.md` for detailed troubleshooting
2. Run `make help` to see all available commands
3. Check container logs: `docker-compose logs -f`
4. Verify Docker is running: `docker ps`

---

## 🎉 Benefits for Your Team

### For Developers:
- ✅ Setup in 5 minutes (vs hours of manual installation)
- ✅ No "works on my machine" issues
- ✅ Easy to reset/clean environment
- ✅ Consistent across all team members

### For DevOps:
- ✅ Production-ready containers
- ✅ Easy to deploy anywhere
- ✅ Scalable architecture
- ✅ Infrastructure as code

### For Project:
- ✅ Faster onboarding for new developers
- ✅ Reduced setup issues
- ✅ Better collaboration
- ✅ Easier CI/CD integration

---

**Happy Coding! 🚀**

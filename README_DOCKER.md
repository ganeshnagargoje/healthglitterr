# Docker Setup Guide for Medical Health Review System

This guide explains how to set up and run the Medical Health Review System with PostgreSQL using Docker.

## Prerequisites

- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- Docker Compose (included with Docker Desktop)

## Quick Start

### 1. Start PostgreSQL Database

Start only the PostgreSQL database:

```bash
docker-compose up -d postgres
```

This will:
- Create a PostgreSQL 16 container
- Initialize the database schema from `init-scripts/01-init-schema.sql`
- Expose PostgreSQL on port 5432 (configurable via `.env`)

### 2. Verify Database is Running

Check the database health:

```bash
docker-compose ps
```

You should see the `medical-health-review-db` container with status "healthy".

### 3. Connect to Database

The database is accessible at:
- **Host**: `localhost`
- **Port**: `5432` (default)
- **Database**: `medical_health_review`
- **User**: `postgres`
- **Password**: `postgres`

Connection string:
```
postgresql://postgres:postgres@localhost:5432/medical_health_review
```

## Optional: pgAdmin (Database Management UI)

To start pgAdmin for database management:

```bash
docker-compose --profile admin up -d pgadmin
```

Access pgAdmin at: http://localhost:5050
- **Email**: `admin@medical-health.local`
- **Password**: `admin`

### Add PostgreSQL Server in pgAdmin

1. Open pgAdmin at http://localhost:5050
2. Right-click "Servers" → "Register" → "Server"
3. General tab:
   - Name: `Medical Health Review DB`
4. Connection tab:
   - Host: `postgres` (use service name, not localhost)
   - Port: `5432`
   - Database: `medical_health_review`
   - Username: `postgres`
   - Password: `postgres`
5. Click "Save"

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key database variables:
```env
POSTGRES_DB=medical_health_review
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/medical_health_review
```

### Custom Ports

To use different ports, update your `.env` file:

```env
POSTGRES_PORT=5433
PGADMIN_PORT=5051
```

Then restart the services:

```bash
docker-compose down
docker-compose up -d
```

## Database Schema

The database schema is automatically initialized from `init-scripts/01-init-schema.sql` when the container first starts. It includes:

- **Tables**: users, medical_reports, health_parameters, normalized_parameters, trends, risk_flags, workflow_states, approval_requests, access_grants, audit_logs, normalization_audit_logs
- **Enums**: user_role, validation_status, normalization_status, trend_direction, risk_level, etc.
- **Indexes**: Optimized for common queries
- **Triggers**: Auto-update timestamps

## Common Commands

### Start all services
```bash
docker-compose up -d
```

### Start with pgAdmin
```bash
docker-compose --profile admin up -d
```

### Stop all services
```bash
docker-compose down
```

### Stop and remove volumes (deletes all data)
```bash
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs -f

# PostgreSQL only
docker-compose logs -f postgres

# pgAdmin only
docker-compose logs -f pgadmin
```

### Access PostgreSQL CLI
```bash
docker-compose exec postgres psql -U postgres -d medical_health_review
```

### Backup database
```bash
docker-compose exec postgres pg_dump -U postgres medical_health_review > backup.sql
```

### Restore database
```bash
docker-compose exec -T postgres psql -U postgres medical_health_review < backup.sql
```

## Running the Application

### Option 1: Run Application Locally (Recommended for Development)

1. Start PostgreSQL with Docker:
   ```bash
   docker-compose up -d postgres
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

### Option 2: Run Application in Docker

Build and run the application container:

```bash
docker build -t medical-health-review .
docker run --network medical-health-network \
  -e DATABASE_URL=postgresql://postgres:postgres@postgres:5432/medical_health_review \
  -v $(pwd)/agentic-medical-health-review:/app/agentic-medical-health-review \
  medical-health-review
```

## Troubleshooting

### Database connection refused

If you get "connection refused" errors:

1. Check if PostgreSQL is running:
   ```bash
   docker-compose ps
   ```

2. Check PostgreSQL logs:
   ```bash
   docker-compose logs postgres
   ```

3. Verify the port is not in use:
   ```bash
   # Windows
   netstat -ano | findstr :5432
   
   # Linux/Mac
   lsof -i :5432
   ```

### Reset database

To completely reset the database:

```bash
docker-compose down -v
docker-compose up -d postgres
```

This will delete all data and reinitialize the schema.

### pgAdmin can't connect to PostgreSQL

When running pgAdmin in Docker, use the service name `postgres` as the host, not `localhost`.

## Database Migrations

For schema changes after initial setup, use Alembic:

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create a migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

## Security Notes

**Important**: The default credentials are for development only. For production:

1. Use strong passwords
2. Don't expose PostgreSQL port publicly
3. Use environment-specific `.env` files
4. Enable SSL/TLS for database connections
5. Implement proper access controls
6. Regular backups

## Next Steps

1. Start the database: `docker-compose up -d postgres`
2. Verify connection: `docker-compose exec postgres psql -U postgres -d medical_health_review -c "SELECT version();"`
3. Run your application with the database connection
4. Implement database access layer using SQLAlchemy (see `requirements.txt`)

## Support

For issues or questions:
- Check Docker logs: `docker-compose logs`
- Verify environment variables in `.env`
- Ensure Docker Desktop is running
- Check port availability

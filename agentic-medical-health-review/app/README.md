# HealthGlitterr AI - Clean Architecture

This directory contains the HealthGlitterr AI application following Clean Architecture principles with explicit SOLID compliance.

## Directory Structure

```
app/
├── domain/                          # Domain Layer (innermost - no external dependencies)
│   ├── entities/                    # Business entities
│   ├── value_objects/               # Immutable value objects
│   ├── repositories/                # Repository interfaces (Ports)
│   └── services/                    # Domain services
│
├── application/                     # Application Layer (use cases)
│   ├── use_cases/                   # Use case implementations
│   └── dtos/                        # Data Transfer Objects
│
├── infrastructure/                  # Infrastructure Layer (adapters)
│   ├── repositories/                # Repository implementations (Adapters)
│   ├── adapters/                    # External service adapters
│   └── database/                    # Database connection
│
├── api/                             # Presentation Layer (FastAPI)
│   └── routes/                      # API routes
│
├── ui/                              # Presentation Layer (React + Vite)
│   └── src/
│       ├── pages/                   # Page components (Login, Dashboard)
│       └── components/              # Shared components (ConsentModal)
│
├── config.py                        # Configuration management
├── logging_config.py                # Logging infrastructure
├── container.py                     # Dependency injection container
└── main.py                          # FastAPI application entry point
```

## Architecture Principles

### Clean Architecture Layers

1. **Domain Layer** (innermost)
   - Contains business logic and entities
   - Framework-independent
   - No dependencies on outer layers
   - Defines repository interfaces (Dependency Inversion)

2. **Application Layer**
   - Orchestrates business workflows (use cases)
   - Depends on domain interfaces
   - Coordinates domain services

3. **Infrastructure Layer**
   - Implements domain interfaces
   - Integrates with external services
   - Handles data persistence

4. **Presentation Layer** (outermost)
   - FastAPI routes (HTTP API)
   - React frontend (Web UI via Vite)
   - Depends on application use cases

### SOLID Principles

- **Single Responsibility Principle (SRP)**: Each component has one reason to change
- **Open/Closed Principle (OCP)**: Open for extension, closed for modification
- **Liskov Substitution Principle (LSP)**: Implementations are substitutable for interfaces
- **Interface Segregation Principle (ISP)**: Focused, minimal interfaces
- **Dependency Inversion Principle (DIP)**: Depend on abstractions, not implementations

## Configuration

Configuration is managed through environment variables. See `.env.example` for all available settings.

Key configuration areas:
- Database connection
- Google OAuth credentials
- API server settings
- File storage settings
- Security settings

## Logging

Logging is configured with:
- Console handler for development
- Rotating file handler for production
- Automatic sanitization of sensitive data
- Structured log format with timestamps

Logs are stored in the `logs/` directory.

## Dependency Injection

The application uses the `dependency-injector` library to manage all dependencies. The container is configured in `container.py` and wires dependencies at runtime.

## Running the Application

### FastAPI Backend

```bash
# From the agentic-medical-health-review directory
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at `http://localhost:8001`

### React Frontend

```bash
# From the agentic-medical-health-review/app/ui directory
npx vite --host
```

The UI will be available at `http://localhost:8000`

The Vite dev server proxies `/api` requests to the FastAPI backend on port 8001.

### Docker (PostgreSQL)

```bash
# From the project root
docker-compose up -d postgres
```

## Development

### Adding New Features

1. Start with the domain layer (entities, services)
2. Define repository interfaces in the domain layer
3. Implement repositories in the infrastructure layer
4. Create use cases in the application layer
5. Add API routes or UI pages in the presentation layer
6. Register dependencies in the container

### Testing

- Unit tests: Test individual components in isolation
- Property tests: Test universal properties with Hypothesis
- Integration tests: Test component interactions
- End-to-end tests: Test complete user workflows

## Security

- OAuth 2.0 authentication with Google
- Session timeout after 30 minutes
- Input sanitization to prevent injection attacks
- Sensitive data excluded from logs
- HTTPS in production
- Temporary file cleanup after processing

## Internationalization

Supported languages:
- English (en)
- Hindi (hi)
- Marathi (mr)
- Tamil (ta)

## License

See the main project LICENSE file.

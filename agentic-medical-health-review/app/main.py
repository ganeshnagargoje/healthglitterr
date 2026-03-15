"""
FastAPI Application Entry Point

This module creates and configures the FastAPI application with
dependency injection and route registration.

SOLID Principles:
- SRP: Only handles application initialization
- DIP: Uses dependency injection for all components
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.container import container
from app.config import config
from app.logging_config import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application with dependency injection
    
    Returns:
        Configured FastAPI application instance
    """
    # Create FastAPI app
    app = FastAPI(
        title="Medical Health Review API",
        description="Backend API for Medical Health Review System with Streamlit UI",
        version="1.0.0",
        debug=config.api.debug
    )
    
    # Attach container to app
    app.container = container
    
    # Configure CORS for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routers
    from app.api.routes.consent import router as consent_router
    from app.api.routes.auth import router as auth_router
    app.include_router(consent_router, prefix="/api/users", tags=["users"])
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "medical-health-review-api"}
    
    logger.info("FastAPI application initialized")
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.debug
    )

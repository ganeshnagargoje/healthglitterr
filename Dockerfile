FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/app/agentic-medical-health-review \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for PDF processing, OCR, and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PDF processing
    poppler-utils \
    # OpenCV and image processing dependencies
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    # PostgreSQL client
    postgresql-client \
    # Build tools (needed for some Python packages)
    gcc \
    g++ \
    make \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and pip config for better Docker layer caching
COPY requirements.txt .
COPY pip.conf /etc/pip.conf

# Install Python dependencies
# Prefer binary wheels to avoid compilation (falls back to source if needed)
# pip.conf enforces binary-only for problematic packages
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --no-deps paddleocr==2.7.0.3

# Copy application code
COPY agentic-medical-health-review/ ./agentic-medical-health-review/
COPY init-scripts/ ./init-scripts/

# Create necessary directories with proper permissions
RUN mkdir -p \
    /app/data \
    /app/agentic-medical-health-review/tools/patient_data_exports \
    /app/agentic-medical-health-review/memory \
    /app/agentic-medical-health-review/agents \
    /app/logs \
    && chmod -R 755 /app

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port for web services
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "from models.database_connection import DatabaseConnection; \
                   with DatabaseConnection() as db: pass" || exit 1

# Default command (can be overridden in docker-compose)
CMD ["python", "-c", "print('Medical Health Review Application Ready')"]


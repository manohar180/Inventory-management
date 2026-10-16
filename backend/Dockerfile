# ==============================================================================
# StockPilot Backend Dockerfile
# Multi-arch slim Python base running as an unprivileged non-root user
# ==============================================================================

FROM python:3.12-slim-bookworm

# Set Python flags for container environments
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create an unprivileged non-root service user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

WORKDIR /app

# Install pinned Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code, Alembic migrations, and config
COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app

# Ensure proper non-root ownership of the working directory
RUN chown -R appuser:appgroup /app

# Switch to unprivileged non-root user
USER appuser

# Expose FastAPI HTTP port
EXPOSE 8000

# Execute database migrations on container startup, then start Uvicorn ASGI server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

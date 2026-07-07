# ============================================
# Nexora Platform — Backend Production Dockerfile
# ============================================
# Multi-stage build for minimal production image

# ---- Stage 1: Build ----
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements/base.txt requirements/base.txt
COPY requirements/prod.txt requirements/prod.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements/prod.txt

# ---- Stage 2: Runtime ----
FROM python:3.12-slim AS runtime

# Security: Run as non-root user
RUN groupadd -r nexora && useradd -r -g nexora -d /app -s /sbin/nologin nexora

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY alembic/ alembic/
COPY alembic.ini .
COPY app/ app/

# Set ownership
RUN chown -R nexora:nexora /app

# Switch to non-root user
USER nexora

# Expose application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Production entrypoint using Gunicorn with Uvicorn workers
CMD ["gunicorn", "app.main:app", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]

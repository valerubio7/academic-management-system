FROM python:3.14.0-alpine3.22

# Build arguments for flexibility
ARG WORKERS=4
ARG TIMEOUT=30
ARG GRACEFUL_TIMEOUT=10
ARG KEEPALIVE=5

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Django settings
    DJANGO_SETTINGS_MODULE=config.settings \
    # Production server settings
    WORKERS=${WORKERS} \
    WORKER_CLASS=sync \
    TIMEOUT=${TIMEOUT} \
    GRACEFUL_TIMEOUT=${GRACEFUL_TIMEOUT} \
    KEEPALIVE=${KEEPALIVE}

WORKDIR /app/

# Install uv, dumb-init for proper signal handling, and PostgreSQL client libraries
COPY --from=ghcr.io/astral-sh/uv:0.9.3 /uv /uvx /bin/
RUN apk add --no-cache \
    dumb-init \
    curl \
    postgresql-libs \
    && apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    postgresql-dev

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app

# Install dependencies (cacheable layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Remove build dependencies
RUN apk del .build-deps

# Copy application code
COPY --chown=appuser:appuser ./config /app/config
COPY --chown=appuser:appuser ./academics /app/academics
COPY --chown=appuser:appuser ./enrollments /app/enrollments
COPY --chown=appuser:appuser ./grading /app/grading
COPY --chown=appuser:appuser ./users /app/users
COPY --chown=appuser:appuser ./static /app/static
COPY --chown=appuser:appuser ./templates /app/templates
COPY --chown=appuser:appuser ./exceptions.py /app/exceptions.py
COPY --chown=appuser:appuser ./manage.py /app/manage.py
COPY --chown=appuser:appuser ./docker-entrypoint.sh /app/docker-entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Note: Skip project installation since we're copying the code directly
# The dependencies are already installed in the previous step

# Note: collectstatic moved to docker-entrypoint.sh to have access to env vars
# RUN python manage.py collectstatic --noinput --clear

# Switch to a non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Use dumb-init to handle signals properly and run migrations before starting
ENTRYPOINT ["/usr/bin/dumb-init", "--", "/app/docker-entrypoint.sh"]

# Run with Gunicorn for production
CMD ["/app/.venv/bin/gunicorn", "config.wsgi:application", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "4", \
    "--timeout", "30", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--log-level", "info", \
    "--limit-request-line", "4094", \
    "--limit-request-fields", "100", \
    "--limit-request-field_size", "8190"]
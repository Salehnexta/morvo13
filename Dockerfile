# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1 – base image with runtime deps
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y build-essential git && \
    pip install --no-cache-dir "poetry==$POETRY_VERSION" && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

# ---------------------------------------------------------------------------
# Stage 2 – install python deps separately for caching
# ---------------------------------------------------------------------------
FROM base AS builder

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --with=prod --without-hashes -o /tmp/requirements.txt && \
    pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

# ---------------------------------------------------------------------------
# Stage 3 – final image
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS final

LABEL org.opencontainers.image.source="https://github.com/your-org/morvo-ai" \
      org.opencontainers.image.description="Morvo AI SaaS Platform"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /opt/app

# Copy installed site-packages from builder layer
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Entrypoint runs migrations then launches the given CMD
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]

# Default command – production server via Gunicorn+Uvicorn worker
CMD gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:"${PORT}" \
    --log-level info 
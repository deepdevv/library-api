# ---------- builder ----------
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    pip install "poetry==${POETRY_VERSION}" && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Only copy dependency manifests first for better layer caching
COPY pyproject.toml poetry.lock* ./

# Install deps (no dev)
RUN poetry install --only main

# Copy the source code last
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY docker ./docker

# ---------- runtime ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    UVICORN_WORKERS=2

# For entrypoint DB wait (pg_isready)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy venv and app from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app
COPY --from=builder /app/alembic /app/alembic
COPY --from=builder /app/alembic.ini /app/alembic.ini
COPY --from=builder /app/docker /app/docker

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/app/docker/entrypoint.sh"]

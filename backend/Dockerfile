# ──────────────────────────────────────────────────────────────────────────────
# d3jusdevspace — Backend Dockerfile
# Multi-stage build: install dependencies with uv, then run with a slim image.
# ──────────────────────────────────────────────────────────────────────────────

# --- Stage 1: Build ---
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

WORKDIR /app

# Install dependencies first (cached layer).
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --frozen

# Copy the application code.
COPY . .

# --- Stage 2: Runtime ---
FROM python:3.14-slim-bookworm

WORKDIR /app

# Copy the virtual environment and app from the builder stage.
COPY --from=builder /app /app

# Add the virtual env to PATH so `uvicorn` is found.
ENV PATH="/app/.venv/bin:$PATH"

# Render injects PORT at runtime (default 10000).
ENV PORT=10000
EXPOSE ${PORT}

# Run uvicorn.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]

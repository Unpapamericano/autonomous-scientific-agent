# Multi-stage build for Autonomous Scientific Research Agent
# Stage 1: Base dependencies
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04 AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    curl \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Stage 2: Python dependencies
FROM base AS dependencies

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir ".[dev]"

# Stage 3: Application
FROM dependencies AS app

WORKDIR /app

# Copy source code
COPY src/ src/
COPY config/ config/
COPY .env.example .env.example
COPY README.md README.md

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "from src.core import MuseGlimmerInference; m = MuseGlimmerInference(); print(m.health_check())" || exit 1

# Default command
CMD ["python3", "-m", "src.core.inference"]

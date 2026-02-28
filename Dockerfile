# Multi-stage build for production-ready image

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir build && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -e "."

# Production stage
FROM python:3.11-slim as production

# Security: Run as non-root user
RUN groupadd -r passgen && useradd -r -g passgen passgen

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi8 \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copy application
COPY src/ /app/src/
COPY README.md /app/

WORKDIR /app

# Change ownership
RUN chown -R passgen:passgen /app

# Switch to non-root user
USER passgen

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/passgen/.local/bin:${PATH}"

# Default command
ENTRYPOINT ["passgen"]
CMD ["--help"]

# Development stage
FROM production as development

USER root

RUN pip install --no-cache-dir -e ".[dev,benchmark]"

USER passgen

# Multi-stage build: keeps the final image small by not shipping build tools.
# Stage 1 builds dependencies; stage 2 copies only what's needed to run.

# ---- Stage 1: builder ----
FROM python:3.12-slim AS builder

WORKDIR /app

# Only copy requirements first so Docker caches this layer unless deps change.
COPY requirements.txt .

# Install only the runtime deps (not the browser test tools) into a venv.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir fastapi==0.115.0 "uvicorn[standard]==0.30.6" pydantic==2.9.0


# ---- Stage 2: runtime ----
FROM python:3.12-slim

WORKDIR /app

# Copy the prepared venv from the builder stage.
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code.
COPY app/ ./app/

# Run as a non-root user for security (a real QA/security concern).
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Healthcheck: Docker will mark the container unhealthy if /health stops
# responding. This is the container-level equivalent of a smoke test.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

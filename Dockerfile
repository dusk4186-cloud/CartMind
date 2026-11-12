# ==============================================================================
#  CartMind — Production Multi-Service Container
#  Runs FastAPI Backend (port 8000) + Streamlit Frontend (port 7860/8501)
# ==============================================================================
FROM python:3.11-slim

# System configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    FASTAPI_PORT=8000 \
    FASTAPI_BASE_URL=http://127.0.0.1:8000 \
    STREAMLIT_SERVER_PORT=7860 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Install curl for container healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Create non-root user (compatible with Hugging Face Spaces UID 1000 standard)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Install Python dependencies first for optimal Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY --chown=appuser:appuser . .

# Ensure entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose default application port (7860 for Hugging Face Spaces / Docker)
EXPOSE 7860

# Healthcheck monitoring the Streamlit UI
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=15s \
    CMD curl -f http://localhost:${PORT}/_stcore/health || exit 1

# Launch both FastAPI backend daemon and Streamlit frontend
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]


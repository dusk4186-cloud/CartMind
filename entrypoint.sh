#!/bin/bash
set -e

echo "=================================================="
echo " Starting CartMind AI Platform"
echo "=================================================="

STREAMLIT_PORT="${PORT:-7860}"
FASTAPI_PORT="${FASTAPI_PORT:-8000}"

# 1. Start FastAPI backend daemon on port 8000
echo "--> Starting FastAPI Mock E-Commerce Backend on port ${FASTAPI_PORT}..."
python -m uvicorn app.main:app --host 127.0.0.1 --port ${FASTAPI_PORT} --log-level warning &
FASTAPI_PID=$!

# 2. Wait for FastAPI to become healthy
echo "--> Waiting for FastAPI backend to become ready..."
MAX_RETRIES=30
COUNT=0
until curl -s http://127.0.0.1:${FASTAPI_PORT}/health > /dev/null; do
    sleep 0.5
    COUNT=$((COUNT+1))
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo "Warning: FastAPI health probe timed out after 15s. Continuing to Streamlit..."
        break
    fi
done
echo "--> FastAPI backend is ready (PID: ${FASTAPI_PID})"

# 3. Start Streamlit in foreground
echo "--> Starting Streamlit Frontend on port ${STREAMLIT_PORT}..."
exec streamlit run streamlit_app.py \
    --server.port "${STREAMLIT_PORT}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false


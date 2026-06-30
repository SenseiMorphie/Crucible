#!/bin/bash

set -e

echo "╔════════════════════════════════════════╗"
echo "║     🚀 Starting Startup Simulator      ║"
echo "╚════════════════════════════════════════╝"
echo ""

echo "Starting FastAPI on port 8000..."
uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 &
BACKEND_PID=$!

echo "Waiting for FastAPI..."
sleep 3

echo "Starting Streamlit on port 8501..."
streamlit run frontend/app.py \
    --server.address 0.0.0.0 \
    --server.port 8501 &
FRONTEND_PID=$!

echo "Waiting for Streamlit..."
sleep 5

echo ""
echo "Starting Nginx..."
echo ""

cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep Nginx in foreground
nginx -g "daemon off;"
#!/bin/bash
# run.sh — Start both backend and frontend in separate terminals

echo "╔════════════════════════════════════════╗"
echo "║         🚀 Startup Simulator           ║"
echo "╚════════════════════════════════════════╝"
echo ""

# # Check .env exists
# if [ ! -f ".env" ]; then
#     echo "⚠️  No .env file found. Copying from .env.example..."
#     cp .env.example .env
#     echo "✏️  Please edit .env and add your API key, then re-run this script."
#     exit 1
# fi

echo "Starting FastAPI backend on http://localhost:8000 ..."
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 3

echo "Starting Streamlit frontend on http://localhost:8501 ..."
streamlit run frontend/app.py &
FRONTEND_PID=$!

echo ""
echo "✅ Both services running!"
echo "   Backend:  http://localhost:8000/docs"
echo "   Frontend: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop both."

# Wait and clean up
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" SIGINT SIGTERM
wait

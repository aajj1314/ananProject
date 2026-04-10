#!/bin/bash
# Start the backend server

set -e

cd "$(dirname "$0")/backend"

# Copy example env if no .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.development.example..."
    cp ../.env.development.example .env
fi

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv ../.venv
fi

# Activate virtual environment
source ../.venv/bin/activate

# Install dependencies if needed
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Starting backend server on http://localhost:8000"
echo "API docs at http://localhost:8000/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

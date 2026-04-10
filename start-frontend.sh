#!/bin/bash
# Start the frontend dev server

set -e

cd "$(dirname "$0")/frontend"

# Copy example env if no .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env 2>/dev/null || true
fi

echo "Installing dependencies..."
npm install

echo "Starting frontend dev server on http://localhost:5173"
npm run dev

# Start the backend server

Set-Location "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\backend"

# Copy example env if no .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.development.example..."
    Copy-Item "..\.env.development.example" ".env"
}

# Check if virtual environment exists
if (-not (Test-Path "..\.venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv "..\.venv"
}

# Activate virtual environment
& "..\.venv\Scripts\Activate.ps1"

# Install dependencies if needed
Write-Host "Installing dependencies..."
pip install -q -r requirements.txt

Write-Host "Starting backend server on http://localhost:8000"
Write-Host "API docs at http://localhost:8000/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
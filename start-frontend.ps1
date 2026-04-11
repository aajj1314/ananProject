# Start the frontend dev server

Set-Location "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\frontend"

# Copy example env if no .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.example..."
    Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
}

Write-Host "Installing dependencies..."
npm install

Write-Host "Starting frontend dev server on http://localhost:8081"
npm run dev
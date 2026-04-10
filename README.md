# Elderly Insole Platform

Full-stack project scaffold for the elderly anti-loss smart insole system.

## Structure

- `backend/`: FastAPI backend
- `frontend/`: Vue 3 + TypeScript frontend
- `deploy/`: containerization assets
- `WORKLOG.md`: phase-by-phase implementation log

## Current Status

This repository is in staged implementation. The first delivery includes:

- backend foundation and API contracts
- authentication flow
- device management flow
- latest location and history endpoints
- frontend project scaffold
- deployment skeleton

## Local Development

Backend defaults to a safe local SQLite async URL when no environment is provided.
Production-style MySQL, Redis, and InfluxDB settings are available through environment variables.

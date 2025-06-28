#!/bin/bash

# Morvo AI Marketing Consultant Startup Script

# Set default environment
export ENVIRONMENT=${ENVIRONMENT:-development}

# Check if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo "Warning: .env file not found. Using default environment variables."
fi

# Check for required environment variables
if [ -z "$JWT_SECRET" ]; then
    echo "Generating random JWT_SECRET..."
    export JWT_SECRET=$(openssl rand -hex 32)
fi

# Check database URL
if [ -z "$DATABASE_URL" ]; then
    echo "DATABASE_URL not set, using SQLite..."
    export DATABASE_URL="sqlite+aiosqlite:///./morvo.db"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting Morvo AI Marketing Consultant..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Deactivate virtual environment on exit
trap "deactivate" EXIT 
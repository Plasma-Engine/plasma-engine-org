#!/bin/bash
# Script to setup minimal working versions of all Plasma Engine services

echo "🚀 Setting up minimal services for Phase 1 testing..."

# Services to setup
services=("content" "brand" "agent")
ports=("8002" "8001" "8003")

for i in "${!services[@]}"; do
    service="${services[$i]}"
    port="${ports[$i]}"
    
    echo "📦 Setting up ${service} service..."
    
    # Create simple requirements
    cat > "plasma-engine-${service}/requirements.txt" << EOF
# Core FastAPI and web framework
fastapi>=0.100.0
uvicorn[standard]>=0.20.0
pydantic>=2.0.0
pydantic-settings

# Database
asyncpg
psycopg2-binary
SQLAlchemy>=2.0.0
alembic
redis

# Basic utilities
loguru
httpx
python-multipart
python-dotenv
aiofiles

# Testing
pytest
pytest-asyncio
EOF
    
    # Create minimal main.py
    cat > "plasma-engine-${service}/app/main.py" << EOF
"""Minimal FastAPI application for ${service} service testing."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="${service^} Service",
    description="Phase 1 ${service^} Service - Minimal Version", 
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "${service}-service",
        "version": "1.0.0", 
        "port": ${port},
        "environment": {
            "DATABASE_URL": bool(os.getenv("DATABASE_URL")),
            "REDIS_URL": bool(os.getenv("REDIS_URL")),
        }
    }

@app.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    return {"status": "ready"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "${service^} Service is running", "docs": "/docs"}

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint."""
    return {
        "api_version": "v1", 
        "service": "${service}",
        "status": "operational"
    }
EOF

    # Fix __init__.py to import app
    cat > "plasma-engine-${service}/app/__init__.py" << EOF
"""Application package for the Plasma Engine ${service^} service."""

from .main import app

__all__ = ["app"]
EOF
    
    echo "✅ ${service^} service setup complete"
done

echo "🎉 All minimal services are ready!"
echo "Next steps:"
echo "1. Build and start services with Docker"
echo "2. Run the test script"
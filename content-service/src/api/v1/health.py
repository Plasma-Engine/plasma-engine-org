"""
Health check API endpoints.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter

from src.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness probe that checks all dependencies.

    Simplified version for initial setup.
    """
    checks = {
        "llm": False,
    }

    # Check LLM availability
    if settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY:
        checks["llm"] = True

    # Determine overall status
    all_healthy = all(checks.values())

    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/live")
async def liveness_check() -> Dict[str, str]:
    """Kubernetes liveness probe endpoint."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }
"""
FastAPI application entry point for Plasma Engine Content Service.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from src.api.v1 import content, templates, health
from src.core.config import settings
from src.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Manage application lifecycle."""
    # Startup
    setup_logging(settings.LOG_LEVEL)

    yield

    # Shutdown
    # Add cleanup logic here if needed


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered content generation service with LangChain",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include API routers
app.include_router(
    health.router,
    tags=["health"],
)

app.include_router(
    content.router,
    prefix="/api/v1",
    tags=["content"],
)

app.include_router(
    templates.router,
    prefix="/api/v1",
    tags=["templates"],
)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
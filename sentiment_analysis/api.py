"""
FastAPI Service for Sentiment Analysis Pipeline (PE-304)
Exposes REST API endpoints for sentiment analysis operations
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client.core import CollectorRegistry
from starlette.responses import Response

from .engine import SentimentEngine, SentimentModel
from .brand_processor import BrandProcessor, BrandProfile
from .scoring import ScoringSystem
from .alerts import AlertSystem, AlertChannel, AlertSeverity
from .pipeline import SentimentPipeline, SocialMediaPost, DataSource
from .integrations import TwitterCollector, RedditCollector, IntegrationManager


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sentiment Analysis API",
    description="Real-time sentiment analysis for brand monitoring (PE-304)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
registry = CollectorRegistry()
request_counter = Counter(
    'sentiment_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)
processing_histogram = Histogram(
    'sentiment_processing_duration_seconds',
    'Processing duration',
    ['operation'],
    registry=registry
)
active_connections = Gauge(
    'sentiment_active_websocket_connections',
    'Active WebSocket connections',
    registry=registry
)

# Global instances (initialized on startup)
sentiment_engine = None
brand_processor = None
scoring_system = None
alert_system = None
pipeline = None
integration_manager = None


# Pydantic models for API
class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="Text to analyze")
    models: Optional[List[str]] = Field(None, description="Models to use")
    extract_aspects: bool = Field(False, description="Extract aspect-based sentiment")
    detect_emotions: bool = Field(False, description="Detect emotions")
    extract_brands: bool = Field(True, description="Extract brand mentions")


class BrandRequest(BaseModel):
    text: str = Field(..., description="Text to analyze")
    source: Optional[str] = Field("api", description="Source of text")


class BatchAnalyzeRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to analyze")
    parallel: bool = Field(True, description="Process in parallel")


class BrandProfileRequest(BaseModel):
    name: str
    aliases: List[str] = []
    hashtags: List[str] = []
    handles: List[str] = []
    competitors: List[str] = []
    products: List[str] = []
    min_confidence: float = 0.7


class AlertChannelRequest(BaseModel):
    name: str
    type: str
    config: Dict[str, Any]
    severity_filter: Optional[List[str]] = None
    enabled: bool = True


class StreamConfig(BaseModel):
    source: str = Field(..., description="Data source (twitter/reddit)")
    filters: Optional[Dict[str, Any]] = None
    batch_size: int = 100


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global sentiment_engine, brand_processor, scoring_system
    global alert_system, pipeline, integration_manager

    logger.info("Initializing sentiment analysis services...")

    # Initialize components
    sentiment_engine = SentimentEngine(
        models=[SentimentModel.VADER, SentimentModel.TEXTBLOB, SentimentModel.ROBERTA]
    )

    brand_processor = BrandProcessor()

    scoring_system = ScoringSystem()

    alert_system = AlertSystem()

    pipeline = SentimentPipeline(
        sentiment_engine=sentiment_engine,
        brand_processor=brand_processor,
        scoring_system=scoring_system,
        alert_system=alert_system
    )

    await pipeline.initialize()

    integration_manager = IntegrationManager(pipeline=pipeline)

    # Load default brand profiles
    try:
        with open('brands.json', 'r') as f:
            brands_data = json.load(f)
            for brand_data in brands_data:
                brand = BrandProfile(**brand_data)
                brand_processor.add_brand(brand)
            logger.info(f"Loaded {len(brands_data)} brand profiles")
    except FileNotFoundError:
        logger.warning("brands.json not found, starting with empty brand list")

    logger.info("Sentiment analysis services initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global pipeline, integration_manager

    if integration_manager:
        await integration_manager.stop()

    if pipeline:
        await pipeline.shutdown()

    logger.info("Sentiment analysis services shut down")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "sentiment_engine": sentiment_engine is not None,
            "brand_processor": brand_processor is not None,
            "pipeline": pipeline is not None
        }
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(registry), media_type="text/plain")


@app.post("/analyze")
async def analyze_text(request: AnalyzeRequest):
    """Analyze sentiment of a single text"""
    try:
        with processing_histogram.labels(operation='analyze').time():
            # Parse model selection
            models = None
            if request.models:
                models = [SentimentModel[m.upper()] for m in request.models]

            # Analyze sentiment
            sentiment = sentiment_engine.analyze(
                request.text,
                models=models,
                extract_aspects=request.extract_aspects,
                detect_emotions=request.detect_emotions
            )

            # Extract brands if requested
            brands = []
            if request.extract_brands:
                brand_mentions = brand_processor.extract_mentions(request.text)
                brands = [
                    {
                        "brand": m.brand,
                        "confidence": m.confidence,
                        "position": m.position
                    }
                    for m in brand_mentions
                ]

            # Calculate scores
            scores = scoring_system.calculate_scores(
                sentiment=sentiment,
                brands=brand_mentions if request.extract_brands else None
            )

            request_counter.labels(method='POST', endpoint='/analyze', status='success').inc()

            return {
                "sentiment": {
                    "label": sentiment.label,
                    "score": sentiment.compound_score,
                    "confidence": sentiment.confidence,
                    "positive": sentiment.positive,
                    "negative": sentiment.negative,
                    "neutral": sentiment.neutral
                },
                "emotions": sentiment.emotions if request.detect_emotions else None,
                "aspects": sentiment.aspects if request.extract_aspects else None,
                "brands": brands,
                "scores": scores
            }

    except Exception as e:
        request_counter.labels(method='POST', endpoint='/analyze', status='error').inc()
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/batch")
async def analyze_batch(request: BatchAnalyzeRequest):
    """Analyze sentiment of multiple texts"""
    try:
        with processing_histogram.labels(operation='batch_analyze').time():
            results = sentiment_engine.analyze_batch(
                request.texts,
                parallel=request.parallel
            )

            request_counter.labels(method='POST', endpoint='/analyze/batch', status='success').inc()

            return {
                "results": [
                    {
                        "text": text,
                        "sentiment": {
                            "label": r.label if r else "ERROR",
                            "score": r.compound_score if r else 0.0,
                            "confidence": r.confidence if r else 0.0
                        }
                    }
                    for text, r in zip(request.texts, results)
                ],
                "total": len(results)
            }

    except Exception as e:
        request_counter.labels(method='POST', endpoint='/analyze/batch', status='error').inc()
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/brands/extract")
async def extract_brands(request: BrandRequest):
    """Extract brand mentions from text"""
    try:
        mentions = brand_processor.extract_mentions(
            request.text,
            source=request.source
        )

        request_counter.labels(method='POST', endpoint='/brands/extract', status='success').inc()

        return {
            "mentions": [
                {
                    "brand": m.brand,
                    "text": m.text,
                    "position": m.position,
                    "confidence": m.confidence,
                    "context": m.context
                }
                for m in mentions
            ],
            "total": len(mentions)
        }

    except Exception as e:
        request_counter.labels(method='POST', endpoint='/brands/extract', status='error').inc()
        logger.error(f"Error extracting brands: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/brands/add")
async def add_brand(brand: BrandProfileRequest):
    """Add a new brand profile"""
    try:
        brand_profile = BrandProfile(**brand.dict())
        brand_processor.add_brand(brand_profile)

        request_counter.labels(method='POST', endpoint='/brands/add', status='success').inc()

        return {"message": f"Brand {brand.name} added successfully"}

    except Exception as e:
        request_counter.labels(method='POST', endpoint='/brands/add', status='error').inc()
        logger.error(f"Error adding brand: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/brands")
async def list_brands():
    """List all configured brands"""
    try:
        brands = [
            {
                "name": b.name,
                "aliases": b.aliases,
                "hashtags": b.hashtags,
                "handles": b.handles,
                "competitors": b.competitors
            }
            for b in brand_processor.brands
        ]

        request_counter.labels(method='GET', endpoint='/brands', status='success').inc()

        return {"brands": brands, "total": len(brands)}

    except Exception as e:
        request_counter.labels(method='GET', endpoint='/brands', status='error').inc()
        logger.error(f"Error listing brands: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/channels/add")
async def add_alert_channel(channel: AlertChannelRequest):
    """Add a new alert channel"""
    try:
        alert_channel = AlertChannel(
            name=channel.name,
            type=channel.type,
            config=channel.config,
            severity_filter=[AlertSeverity[s.upper()] for s in (channel.severity_filter or [])],
            enabled=channel.enabled
        )

        alert_system.add_channel(alert_channel)

        request_counter.labels(method='POST', endpoint='/alerts/channels/add', status='success').inc()

        return {"message": f"Alert channel {channel.name} added successfully"}

    except Exception as e:
        request_counter.labels(method='POST', endpoint='/alerts/channels/add', status='error').inc()
        logger.error(f"Error adding alert channel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts/stats")
async def alert_statistics():
    """Get alert statistics"""
    try:
        stats = alert_system.get_alert_statistics()

        request_counter.labels(method='GET', endpoint='/alerts/stats', status='success').inc()

        return stats

    except Exception as e:
        request_counter.labels(method='GET', endpoint='/alerts/stats', status='error').inc()
        logger.error(f"Error getting alert stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream/start")
async def start_stream(config: StreamConfig, background_tasks: BackgroundTasks):
    """Start streaming data processing"""
    try:
        # Create collector based on source
        if config.source.lower() == 'twitter':
            collector = TwitterCollector(filters=config.filters)
        elif config.source.lower() == 'reddit':
            collector = RedditCollector(
                subreddits=config.filters.get('subreddits', []) if config.filters else []
            )
        else:
            raise ValueError(f"Unknown source: {config.source}")

        # Add to integration manager
        integration_manager.add_collector(config.source, collector)

        # Start processing in background
        background_tasks.add_task(
            integration_manager.start
        )

        request_counter.labels(method='POST', endpoint='/stream/start', status='success').inc()

        return {"message": f"Stream processing started for {config.source}"}

    except Exception as e:
        request_counter.labels(method='POST', endpoint='/stream/start', status='error').inc()
        logger.error(f"Error starting stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream/stop")
async def stop_stream():
    """Stop streaming data processing"""
    try:
        await integration_manager.stop()

        request_counter.labels(method='POST', endpoint='/stream/stop', status='success').inc()

        return {"message": "Stream processing stopped"}

    except Exception as e:
        request_counter.labels(method='POST', endpoint='/stream/stop', status='error').inc()
        logger.error(f"Error stopping stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pipeline/stats")
async def pipeline_statistics():
    """Get pipeline processing statistics"""
    try:
        stats = pipeline.get_stats()

        request_counter.labels(method='GET', endpoint='/pipeline/stats', status='success').inc()

        return stats

    except Exception as e:
        request_counter.labels(method='GET', endpoint='/pipeline/stats', status='error').inc()
        logger.error(f"Error getting pipeline stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket for real-time updates
@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time sentiment updates"""
    await websocket.accept()
    active_connections.inc()

    try:
        # Send updates via WebSocket
        async def send_update(processed):
            await websocket.send_json({
                "timestamp": datetime.now().isoformat(),
                "post_id": processed.post.id,
                "text": processed.post.text[:200],
                "sentiment": processed.sentiment.label,
                "score": processed.sentiment.compound_score,
                "brands": [b.brand for b in processed.brands],
                "alerts": [
                    {
                        "severity": a.severity.value,
                        "message": a.message
                    }
                    for a in processed.alerts
                ]
            })

        # Process stream with WebSocket callback
        # This would be connected to actual streaming data
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
                else:
                    # Process received text
                    result = sentiment_engine.analyze(data)
                    await websocket.send_json({
                        "sentiment": result.label,
                        "score": result.compound_score
                    })
            except WebSocketDisconnect:
                break

    finally:
        active_connections.dec()
        logger.info("WebSocket connection closed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
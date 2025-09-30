"""
Sentiment Analysis Pipeline for Brand Monitoring
PE-304: Multi-model sentiment analysis with real-time processing
"""

from .engine import SentimentEngine
from .brand_processor import BrandProcessor
from .pipeline import SentimentPipeline
from .alerts import AlertSystem
from .scoring import ScoringSystem

__version__ = "1.0.0"
__all__ = [
    "SentimentEngine",
    "BrandProcessor",
    "SentimentPipeline",
    "AlertSystem",
    "ScoringSystem"
]
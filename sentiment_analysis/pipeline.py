"""
Real-time Sentiment Analysis Pipeline
Processes streaming data from social media sources
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
import json
from enum import Enum
import aioredis
from concurrent.futures import ThreadPoolExecutor
import queue
import threading


from .engine import SentimentEngine, SentimentResult, SentimentModel
from .brand_processor import BrandProcessor, BrandMention, BrandProfile
from .scoring import ScoringSystem
from .alerts import AlertSystem, Alert, AlertSeverity


logger = logging.getLogger(__name__)


class DataSource(Enum):
    TWITTER = "twitter"
    REDDIT = "reddit"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    NEWS = "news"
    CUSTOM = "custom"


@dataclass
class SocialMediaPost:
    id: str
    text: str
    source: DataSource
    timestamp: datetime
    author: str = ""
    url: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    engagement: Dict[str, int] = field(default_factory=dict)  # likes, shares, comments


@dataclass
class ProcessedPost:
    post: SocialMediaPost
    sentiment: SentimentResult
    brands: List[BrandMention]
    scores: Dict[str, float]
    alerts: List[Alert] = field(default_factory=list)
    processing_time: float = 0.0


class SentimentPipeline:
    """
    Real-time sentiment analysis pipeline for social media data
    Handles streaming data, batch processing, and alert generation
    """

    def __init__(
        self,
        sentiment_engine: SentimentEngine = None,
        brand_processor: BrandProcessor = None,
        scoring_system: ScoringSystem = None,
        alert_system: AlertSystem = None,
        batch_size: int = 100,
        buffer_size: int = 10000,
        redis_url: str = None,
        max_workers: int = 4
    ):
        self.sentiment_engine = sentiment_engine or SentimentEngine()
        self.brand_processor = brand_processor or BrandProcessor()
        self.scoring_system = scoring_system or ScoringSystem()
        self.alert_system = alert_system or AlertSystem()

        self.batch_size = batch_size
        self.buffer_size = buffer_size
        self.redis_url = redis_url
        self.max_workers = max_workers

        # Processing buffers
        self.input_buffer = asyncio.Queue(maxsize=buffer_size)
        self.output_buffer = asyncio.Queue(maxsize=buffer_size)
        self.processing_stats = defaultdict(int)

        # Thread pool for CPU-intensive tasks
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Redis for distributed processing
        self.redis_client = None

        # Processing state
        self.is_running = False
        self.tasks = []

        logger.info("SentimentPipeline initialized")

    async def initialize(self):
        """Initialize pipeline resources"""
        if self.redis_url:
            try:
                self.redis_client = await aioredis.create_redis_pool(self.redis_url)
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")

        logger.info("Pipeline initialized and ready")

    async def shutdown(self):
        """Cleanup pipeline resources"""
        self.is_running = False

        # Cancel all tasks
        for task in self.tasks:
            task.cancel()

        # Close Redis connection
        if self.redis_client:
            self.redis_client.close()
            await self.redis_client.wait_closed()

        # Shutdown executor
        self.executor.shutdown(wait=True)

        logger.info("Pipeline shut down")

    async def process_stream(
        self,
        stream: AsyncIterator[SocialMediaPost],
        output_callback: Optional[Callable] = None
    ):
        """
        Process a stream of social media posts in real-time

        Args:
            stream: Async iterator of posts
            output_callback: Callback for processed posts
        """
        self.is_running = True

        # Start processing tasks
        self.tasks = [
            asyncio.create_task(self._input_processor(stream)),
            asyncio.create_task(self._batch_processor()),
            asyncio.create_task(self._output_processor(output_callback)),
            asyncio.create_task(self._stats_reporter())
        ]

        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            logger.info("Stream processing cancelled")
        except Exception as e:
            logger.error(f"Stream processing error: {e}")
            raise

    async def _input_processor(self, stream: AsyncIterator[SocialMediaPost]):
        """Read posts from stream and add to input buffer"""
        try:
            async for post in stream:
                if not self.is_running:
                    break

                await self.input_buffer.put(post)
                self.processing_stats['posts_received'] += 1

                # Store in Redis if available
                if self.redis_client:
                    await self._store_post_redis(post)

        except Exception as e:
            logger.error(f"Input processing error: {e}")
            raise

    async def _batch_processor(self):
        """Process posts in batches for efficiency"""
        batch = []

        while self.is_running or not self.input_buffer.empty():
            try:
                # Collect batch
                timeout = 1.0 if self.is_running else 0.1

                while len(batch) < self.batch_size:
                    try:
                        post = await asyncio.wait_for(
                            self.input_buffer.get(),
                            timeout=timeout
                        )
                        batch.append(post)
                    except asyncio.TimeoutError:
                        break

                if batch:
                    # Process batch
                    processed_batch = await self._process_batch(batch)

                    # Add to output buffer
                    for processed in processed_batch:
                        await self.output_buffer.put(processed)

                    self.processing_stats['batches_processed'] += 1
                    self.processing_stats['posts_processed'] += len(batch)

                    batch = []

                await asyncio.sleep(0.01)  # Small delay to prevent CPU hogging

            except Exception as e:
                logger.error(f"Batch processing error: {e}")
                # Don't lose the batch
                for post in batch:
                    await self.input_buffer.put(post)
                batch = []

    async def _process_batch(self, posts: List[SocialMediaPost]) -> List[ProcessedPost]:
        """Process a batch of posts"""
        loop = asyncio.get_event_loop()

        # Run CPU-intensive processing in thread pool
        processed = await loop.run_in_executor(
            self.executor,
            self._process_batch_sync,
            posts
        )

        return processed

    def _process_batch_sync(self, posts: List[SocialMediaPost]) -> List[ProcessedPost]:
        """Synchronous batch processing (runs in thread pool)"""
        import time
        processed_posts = []

        for post in posts:
            start_time = time.time()

            # Extract brand mentions
            brands = self.brand_processor.extract_mentions(
                post.text,
                source=post.source.value
            )

            # Analyze sentiment
            sentiment = self.sentiment_engine.analyze(
                post.text,
                extract_aspects=True,
                detect_emotions=True
            )

            # Calculate scores
            scores = self.scoring_system.calculate_scores(
                sentiment=sentiment,
                brands=brands,
                engagement=post.engagement
            )

            # Check for alerts
            alerts = self.alert_system.check_thresholds(
                post=post,
                sentiment=sentiment,
                scores=scores,
                brands=brands
            )

            # Create processed post
            processed = ProcessedPost(
                post=post,
                sentiment=sentiment,
                brands=brands,
                scores=scores,
                alerts=alerts,
                processing_time=time.time() - start_time
            )

            processed_posts.append(processed)

        return processed_posts

    async def _output_processor(self, callback: Optional[Callable] = None):
        """Handle processed posts"""
        while self.is_running or not self.output_buffer.empty():
            try:
                timeout = 1.0 if self.is_running else 0.1
                processed = await asyncio.wait_for(
                    self.output_buffer.get(),
                    timeout=timeout
                )

                # Store results
                await self._store_results(processed)

                # Trigger alerts if any
                if processed.alerts:
                    await self._handle_alerts(processed)

                # Call user callback
                if callback:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(processed)
                    else:
                        callback(processed)

                self.processing_stats['posts_output'] += 1

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Output processing error: {e}")

    async def _store_post_redis(self, post: SocialMediaPost):
        """Store post in Redis for distributed processing"""
        if not self.redis_client:
            return

        key = f"post:{post.source.value}:{post.id}"
        value = json.dumps({
            'id': post.id,
            'text': post.text,
            'source': post.source.value,
            'timestamp': post.timestamp.isoformat(),
            'author': post.author,
            'url': post.url,
            'metadata': post.metadata,
            'engagement': post.engagement
        })

        await self.redis_client.setex(key, 86400, value)  # 24 hour TTL

    async def _store_results(self, processed: ProcessedPost):
        """Store processed results"""
        if not self.redis_client:
            return

        key = f"result:{processed.post.source.value}:{processed.post.id}"
        value = json.dumps({
            'post_id': processed.post.id,
            'sentiment': {
                'label': processed.sentiment.label,
                'score': processed.sentiment.compound_score,
                'confidence': processed.sentiment.confidence
            },
            'brands': [
                {
                    'brand': b.brand,
                    'confidence': b.confidence
                }
                for b in processed.brands
            ],
            'scores': processed.scores,
            'alerts': [
                {
                    'severity': a.severity.value,
                    'message': a.message
                }
                for a in processed.alerts
            ],
            'processing_time': processed.processing_time
        })

        await self.redis_client.setex(key, 86400, value)  # 24 hour TTL

    async def _handle_alerts(self, processed: ProcessedPost):
        """Handle generated alerts"""
        for alert in processed.alerts:
            # Log alert
            logger.warning(f"Alert: {alert.severity.value} - {alert.message}")

            # Store alert in Redis
            if self.redis_client:
                alert_key = f"alert:{alert.id}"
                alert_value = json.dumps({
                    'id': alert.id,
                    'severity': alert.severity.value,
                    'type': alert.type,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'post_id': processed.post.id,
                    'metadata': alert.metadata
                })
                await self.redis_client.setex(alert_key, 86400, alert_value)

            # Trigger alert handlers
            await self.alert_system.send_alert(alert)

    async def _stats_reporter(self):
        """Report processing statistics periodically"""
        while self.is_running:
            await asyncio.sleep(60)  # Report every minute

            stats = {
                'timestamp': datetime.now().isoformat(),
                'posts_received': self.processing_stats['posts_received'],
                'posts_processed': self.processing_stats['posts_processed'],
                'posts_output': self.processing_stats['posts_output'],
                'batches_processed': self.processing_stats['batches_processed'],
                'input_buffer_size': self.input_buffer.qsize(),
                'output_buffer_size': self.output_buffer.qsize()
            }

            # Calculate rates
            if self.processing_stats['posts_processed'] > 0:
                stats['avg_batch_size'] = (
                    self.processing_stats['posts_processed'] /
                    max(1, self.processing_stats['batches_processed'])
                )

            logger.info(f"Pipeline stats: {json.dumps(stats)}")

            # Store in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    'pipeline:stats:latest',
                    3600,
                    json.dumps(stats)
                )

    async def process_historical(
        self,
        posts: List[SocialMediaPost],
        parallel: bool = True
    ) -> List[ProcessedPost]:
        """
        Process historical posts (non-streaming)

        Args:
            posts: List of posts to process
            parallel: Whether to process in parallel

        Returns:
            List of processed posts
        """
        if not posts:
            return []

        loop = asyncio.get_event_loop()

        if parallel:
            # Process in batches
            results = []
            for i in range(0, len(posts), self.batch_size):
                batch = posts[i:i + self.batch_size]
                processed = await loop.run_in_executor(
                    self.executor,
                    self._process_batch_sync,
                    batch
                )
                results.extend(processed)
            return results
        else:
            # Process sequentially
            return await loop.run_in_executor(
                self.executor,
                self._process_batch_sync,
                posts
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get current pipeline statistics"""
        return {
            'posts_received': self.processing_stats['posts_received'],
            'posts_processed': self.processing_stats['posts_processed'],
            'posts_output': self.processing_stats['posts_output'],
            'batches_processed': self.processing_stats['batches_processed'],
            'input_buffer_size': self.input_buffer.qsize(),
            'output_buffer_size': self.output_buffer.qsize(),
            'is_running': self.is_running
        }
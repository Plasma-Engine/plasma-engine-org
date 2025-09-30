"""
Integration interfaces for social media collectors
Connects to Twitter (PE-302) and Reddit (PE-303) monitoring systems
"""

import asyncio
import logging
from typing import AsyncIterator, Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
import json
import aiohttp
import aioredis
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError


from .pipeline import SocialMediaPost, DataSource, SentimentPipeline


logger = logging.getLogger(__name__)


class CollectorInterface(ABC):
    """Abstract base class for social media collectors"""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the data source"""
        pass

    @abstractmethod
    async def disconnect(self):
        """Disconnect from the data source"""
        pass

    @abstractmethod
    async def stream(self) -> AsyncIterator[SocialMediaPost]:
        """Stream posts from the source"""
        pass

    @abstractmethod
    async def fetch_batch(self, count: int = 100) -> List[SocialMediaPost]:
        """Fetch a batch of posts"""
        pass


class TwitterCollector(CollectorInterface):
    """
    Interface for Twitter/X data collection (PE-302)
    Connects to the Twitter streaming API and processes tweets
    """

    def __init__(
        self,
        api_endpoint: str = None,
        kafka_topic: str = "twitter-stream",
        redis_url: str = None,
        filters: Dict[str, Any] = None
    ):
        self.api_endpoint = api_endpoint or "http://plasma-engine-twitter:8002"
        self.kafka_topic = kafka_topic
        self.redis_url = redis_url
        self.filters = filters or {}

        self.session = None
        self.redis_client = None
        self.kafka_consumer = None
        self.is_connected = False

        logger.info("TwitterCollector initialized")

    async def connect(self) -> bool:
        """Connect to Twitter data sources"""
        try:
            # Connect to API
            self.session = aiohttp.ClientSession()

            # Connect to Redis if configured
            if self.redis_url:
                self.redis_client = await aioredis.create_redis_pool(self.redis_url)

            # Connect to Kafka if configured
            if self.kafka_topic:
                self.kafka_consumer = KafkaConsumer(
                    self.kafka_topic,
                    bootstrap_servers=['localhost:9092'],
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    auto_offset_reset='latest',
                    enable_auto_commit=True,
                    group_id='sentiment-analysis'
                )

            self.is_connected = True
            logger.info("TwitterCollector connected successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to connect TwitterCollector: {e}")
            return False

    async def disconnect(self):
        """Disconnect from Twitter data sources"""
        if self.session:
            await self.session.close()

        if self.redis_client:
            self.redis_client.close()
            await self.redis_client.wait_closed()

        if self.kafka_consumer:
            self.kafka_consumer.close()

        self.is_connected = False
        logger.info("TwitterCollector disconnected")

    async def stream(self) -> AsyncIterator[SocialMediaPost]:
        """Stream tweets in real-time"""
        if not self.is_connected:
            await self.connect()

        # Stream from Kafka if available
        if self.kafka_consumer:
            async for tweet_data in self._stream_from_kafka():
                yield self._parse_tweet(tweet_data)
        # Stream from API
        elif self.session:
            async for tweet_data in self._stream_from_api():
                yield self._parse_tweet(tweet_data)
        else:
            logger.error("No data source available for streaming")

    async def _stream_from_kafka(self):
        """Stream tweets from Kafka"""
        loop = asyncio.get_event_loop()

        while self.is_connected:
            # Run Kafka consumer in executor (it's blocking)
            messages = await loop.run_in_executor(
                None,
                lambda: self.kafka_consumer.poll(timeout_ms=1000)
            )

            for topic_partition, records in messages.items():
                for record in records:
                    yield record.value

    async def _stream_from_api(self):
        """Stream tweets from API endpoint"""
        url = f"{self.api_endpoint}/stream"
        params = self.filters

        async with self.session.get(url, params=params) as response:
            async for line in response.content:
                if line:
                    try:
                        tweet_data = json.loads(line)
                        yield tweet_data
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse tweet: {line}")

    async def fetch_batch(self, count: int = 100) -> List[SocialMediaPost]:
        """Fetch a batch of recent tweets"""
        if not self.is_connected:
            await self.connect()

        tweets = []

        # Try Redis first
        if self.redis_client:
            keys = await self.redis_client.keys('tweet:*', encoding='utf-8')
            for key in keys[:count]:
                data = await self.redis_client.get(key, encoding='utf-8')
                if data:
                    tweet_data = json.loads(data)
                    tweets.append(self._parse_tweet(tweet_data))

        # Fallback to API
        if len(tweets) < count and self.session:
            url = f"{self.api_endpoint}/tweets"
            params = {'count': count - len(tweets), **self.filters}

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    for tweet_data in data.get('tweets', []):
                        tweets.append(self._parse_tweet(tweet_data))

        return tweets

    def _parse_tweet(self, data: Dict[str, Any]) -> SocialMediaPost:
        """Parse tweet data into SocialMediaPost"""
        return SocialMediaPost(
            id=data.get('id', ''),
            text=data.get('text', ''),
            source=DataSource.TWITTER,
            timestamp=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            author=data.get('author', {}).get('username', ''),
            url=f"https://twitter.com/{data.get('author', {}).get('username', '')}/status/{data.get('id', '')}",
            metadata={
                'author_id': data.get('author', {}).get('id'),
                'author_followers': data.get('author', {}).get('followers_count', 0),
                'author_verified': data.get('author', {}).get('verified', False),
                'lang': data.get('lang', 'en'),
                'hashtags': data.get('hashtags', []),
                'mentions': data.get('mentions', [])
            },
            engagement={
                'likes': data.get('public_metrics', {}).get('like_count', 0),
                'shares': data.get('public_metrics', {}).get('retweet_count', 0),
                'comments': data.get('public_metrics', {}).get('reply_count', 0),
                'views': data.get('public_metrics', {}).get('impression_count', 0)
            }
        )


class RedditCollector(CollectorInterface):
    """
    Interface for Reddit data collection (PE-303)
    Connects to Reddit API and processes posts/comments
    """

    def __init__(
        self,
        api_endpoint: str = None,
        kafka_topic: str = "reddit-stream",
        redis_url: str = None,
        subreddits: List[str] = None
    ):
        self.api_endpoint = api_endpoint or "http://plasma-engine-reddit:8003"
        self.kafka_topic = kafka_topic
        self.redis_url = redis_url
        self.subreddits = subreddits or []

        self.session = None
        self.redis_client = None
        self.kafka_consumer = None
        self.is_connected = False

        logger.info(f"RedditCollector initialized for subreddits: {self.subreddits}")

    async def connect(self) -> bool:
        """Connect to Reddit data sources"""
        try:
            # Connect to API
            self.session = aiohttp.ClientSession()

            # Connect to Redis if configured
            if self.redis_url:
                self.redis_client = await aioredis.create_redis_pool(self.redis_url)

            # Connect to Kafka if configured
            if self.kafka_topic:
                self.kafka_consumer = KafkaConsumer(
                    self.kafka_topic,
                    bootstrap_servers=['localhost:9092'],
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    auto_offset_reset='latest',
                    enable_auto_commit=True,
                    group_id='sentiment-analysis'
                )

            self.is_connected = True
            logger.info("RedditCollector connected successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to connect RedditCollector: {e}")
            return False

    async def disconnect(self):
        """Disconnect from Reddit data sources"""
        if self.session:
            await self.session.close()

        if self.redis_client:
            self.redis_client.close()
            await self.redis_client.wait_closed()

        if self.kafka_consumer:
            self.kafka_consumer.close()

        self.is_connected = False
        logger.info("RedditCollector disconnected")

    async def stream(self) -> AsyncIterator[SocialMediaPost]:
        """Stream Reddit posts/comments in real-time"""
        if not self.is_connected:
            await self.connect()

        # Stream from Kafka if available
        if self.kafka_consumer:
            async for post_data in self._stream_from_kafka():
                yield self._parse_reddit_post(post_data)
        # Stream from API
        elif self.session:
            async for post_data in self._stream_from_api():
                yield self._parse_reddit_post(post_data)
        else:
            logger.error("No data source available for streaming")

    async def _stream_from_kafka(self):
        """Stream Reddit posts from Kafka"""
        loop = asyncio.get_event_loop()

        while self.is_connected:
            messages = await loop.run_in_executor(
                None,
                lambda: self.kafka_consumer.poll(timeout_ms=1000)
            )

            for topic_partition, records in messages.items():
                for record in records:
                    yield record.value

    async def _stream_from_api(self):
        """Stream Reddit posts from API endpoint"""
        url = f"{self.api_endpoint}/stream"
        params = {'subreddits': ','.join(self.subreddits)} if self.subreddits else {}

        async with self.session.get(url, params=params) as response:
            async for line in response.content:
                if line:
                    try:
                        post_data = json.loads(line)
                        yield post_data
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse Reddit post: {line}")

    async def fetch_batch(self, count: int = 100) -> List[SocialMediaPost]:
        """Fetch a batch of recent Reddit posts"""
        if not self.is_connected:
            await self.connect()

        posts = []

        # Try Redis first
        if self.redis_client:
            keys = await self.redis_client.keys('reddit:*', encoding='utf-8')
            for key in keys[:count]:
                data = await self.redis_client.get(key, encoding='utf-8')
                if data:
                    post_data = json.loads(data)
                    posts.append(self._parse_reddit_post(post_data))

        # Fallback to API
        if len(posts) < count and self.session:
            url = f"{self.api_endpoint}/posts"
            params = {
                'count': count - len(posts),
                'subreddits': ','.join(self.subreddits)
            } if self.subreddits else {'count': count - len(posts)}

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    for post_data in data.get('posts', []):
                        posts.append(self._parse_reddit_post(post_data))

        return posts

    def _parse_reddit_post(self, data: Dict[str, Any]) -> SocialMediaPost:
        """Parse Reddit post/comment data into SocialMediaPost"""
        # Determine if it's a post or comment
        is_comment = data.get('type') == 'comment'

        text = data.get('title', '') + ' ' + data.get('body', '') if not is_comment else data.get('body', '')

        return SocialMediaPost(
            id=data.get('id', ''),
            text=text.strip(),
            source=DataSource.REDDIT,
            timestamp=datetime.fromtimestamp(data.get('created_utc', datetime.now().timestamp())),
            author=data.get('author', ''),
            url=data.get('permalink', ''),
            metadata={
                'subreddit': data.get('subreddit', ''),
                'type': 'comment' if is_comment else 'post',
                'flair': data.get('link_flair_text', ''),
                'is_self': data.get('is_self', False),
                'author_karma': data.get('author_karma', 0),
                'gilded': data.get('gilded', 0)
            },
            engagement={
                'likes': data.get('score', 0),
                'comments': data.get('num_comments', 0),
                'shares': data.get('num_crossposts', 0),
                'views': data.get('view_count', 0)
            }
        )


class IntegrationManager:
    """
    Manages multiple social media collectors and routes data to sentiment pipeline
    """

    def __init__(
        self,
        pipeline: SentimentPipeline,
        collectors: Dict[str, CollectorInterface] = None
    ):
        self.pipeline = pipeline
        self.collectors = collectors or {}
        self.tasks = []
        self.is_running = False

        logger.info(f"IntegrationManager initialized with {len(self.collectors)} collectors")

    def add_collector(self, name: str, collector: CollectorInterface):
        """Add a new collector"""
        self.collectors[name] = collector
        logger.info(f"Added collector: {name}")

    async def start(self, output_callback: Optional[Callable] = None):
        """Start all collectors and begin processing"""
        self.is_running = True

        # Initialize pipeline
        await self.pipeline.initialize()

        # Connect all collectors
        for name, collector in self.collectors.items():
            connected = await collector.connect()
            if not connected:
                logger.error(f"Failed to connect collector: {name}")

        # Create merged stream
        merged_stream = self._merge_streams()

        # Start pipeline processing
        await self.pipeline.process_stream(merged_stream, output_callback)

    async def stop(self):
        """Stop all collectors and pipeline"""
        self.is_running = False

        # Disconnect collectors
        for name, collector in self.collectors.items():
            await collector.disconnect()

        # Shutdown pipeline
        await self.pipeline.shutdown()

        logger.info("IntegrationManager stopped")

    async def _merge_streams(self) -> AsyncIterator[SocialMediaPost]:
        """Merge streams from all collectors"""
        queues = []

        # Create queue for each collector
        for name, collector in self.collectors.items():
            queue = asyncio.Queue()
            queues.append(queue)

            # Start collector task
            task = asyncio.create_task(
                self._collector_task(name, collector, queue)
            )
            self.tasks.append(task)

        # Merge queues
        while self.is_running:
            for queue in queues:
                try:
                    post = await asyncio.wait_for(queue.get(), timeout=0.1)
                    yield post
                except asyncio.TimeoutError:
                    continue

    async def _collector_task(
        self,
        name: str,
        collector: CollectorInterface,
        queue: asyncio.Queue
    ):
        """Task for running a collector"""
        try:
            async for post in collector.stream():
                if not self.is_running:
                    break
                await queue.put(post)
        except Exception as e:
            logger.error(f"Error in collector {name}: {e}")

    async def process_historical(
        self,
        collector_name: str,
        count: int = 1000
    ) -> Dict[str, Any]:
        """Process historical data from a specific collector"""
        if collector_name not in self.collectors:
            logger.error(f"Collector not found: {collector_name}")
            return {}

        collector = self.collectors[collector_name]

        # Connect if needed
        if not hasattr(collector, 'is_connected') or not collector.is_connected:
            await collector.connect()

        # Fetch batch
        posts = await collector.fetch_batch(count)

        # Process through pipeline
        processed = await self.pipeline.process_historical(posts)

        # Analyze results
        results = {
            'total_processed': len(processed),
            'sentiment_distribution': {},
            'brands_found': [],
            'alerts_generated': []
        }

        for p in processed:
            # Count sentiment
            sentiment = p.sentiment.label
            results['sentiment_distribution'][sentiment] = results['sentiment_distribution'].get(sentiment, 0) + 1

            # Collect brands
            for brand in p.brands:
                if brand.brand not in results['brands_found']:
                    results['brands_found'].append(brand.brand)

            # Collect alerts
            for alert in p.alerts:
                results['alerts_generated'].append({
                    'type': alert.type.value,
                    'severity': alert.severity.value,
                    'message': alert.message
                })

        return results
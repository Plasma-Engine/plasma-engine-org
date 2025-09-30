"""
Performance Optimization Module for Semantic Search (PE-205)
Implements caching, batching, and performance enhancements
"""

import asyncio
import hashlib
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache, wraps
from dataclasses import dataclass
import numpy as np
import redis.asyncio as redis
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Track and report performance metrics"""

    def __init__(self):
        self.query_times = []
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_queries = 0
        self.batch_sizes = []

    def record_query_time(self, duration: float):
        """Record query execution time"""
        self.query_times.append(duration)
        self.total_queries += 1

    def record_cache_hit(self):
        """Record a cache hit"""
        self.cache_hits += 1

    def record_cache_miss(self):
        """Record a cache miss"""
        self.cache_misses += 1

    def record_batch_size(self, size: int):
        """Record batch processing size"""
        self.batch_sizes.append(size)

    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        avg_query_time = np.mean(self.query_times) if self.query_times else 0
        p95_query_time = np.percentile(self.query_times, 95) if self.query_times else 0
        p99_query_time = np.percentile(self.query_times, 99) if self.query_times else 0

        cache_hit_rate = (
            self.cache_hits / (self.cache_hits + self.cache_misses)
            if (self.cache_hits + self.cache_misses) > 0
            else 0
        )

        return {
            "total_queries": self.total_queries,
            "average_query_time_ms": avg_query_time * 1000,
            "p95_query_time_ms": p95_query_time * 1000,
            "p99_query_time_ms": p99_query_time * 1000,
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "average_batch_size": np.mean(self.batch_sizes) if self.batch_sizes else 0
        }


class RedisCache:
    """Redis-based cache for embeddings and search results"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.client = None
        self.ttl = 3600  # 1 hour default TTL

    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = await redis.from_url(self.redis_url)
            await self.client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()

    def _generate_key(self, prefix: str, data: str) -> str:
        """Generate cache key"""
        hash_digest = hashlib.sha256(data.encode()).hexdigest()[:16]
        return f"semantic_search:{prefix}:{hash_digest}"

    async def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get cached embedding"""
        if not self.client:
            return None

        try:
            key = self._generate_key("embedding", text)
            data = await self.client.get(key)
            if data:
                return np.frombuffer(data, dtype=np.float32)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None

    async def set_embedding(self, text: str, embedding: np.ndarray):
        """Cache an embedding"""
        if not self.client:
            return

        try:
            key = self._generate_key("embedding", text)
            await self.client.setex(
                key,
                self.ttl,
                embedding.astype(np.float32).tobytes()
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    async def get_search_results(self, query_hash: str) -> Optional[List[Dict]]:
        """Get cached search results"""
        if not self.client:
            return None

        try:
            key = f"semantic_search:results:{query_hash}"
            data = await self.client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None

    async def set_search_results(self, query_hash: str, results: List[Dict]):
        """Cache search results"""
        if not self.client:
            return

        try:
            key = f"semantic_search:results:{query_hash}"
            await self.client.setex(
                key,
                self.ttl // 2,  # Shorter TTL for search results
                json.dumps(results)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")


class BatchProcessor:
    """Process embeddings and searches in batches for efficiency"""

    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.pending_embeddings = []
        self.pending_searches = []
        self.processing_lock = asyncio.Lock()

    async def add_embedding_request(self, text: str) -> asyncio.Future:
        """Add an embedding request to the batch"""
        future = asyncio.Future()
        self.pending_embeddings.append((text, future))

        # Process batch if it's full
        if len(self.pending_embeddings) >= self.batch_size:
            await self.process_embedding_batch()

        return future

    async def process_embedding_batch(self):
        """Process a batch of embedding requests"""
        async with self.processing_lock:
            if not self.pending_embeddings:
                return

            batch = self.pending_embeddings[:self.batch_size]
            self.pending_embeddings = self.pending_embeddings[self.batch_size:]

            try:
                # In production, this would call the embedding service
                # For now, generate mock embeddings
                texts = [item[0] for item in batch]
                embeddings = await self._batch_generate_embeddings(texts)

                # Resolve futures
                for (text, future), embedding in zip(batch, embeddings):
                    future.set_result(embedding)

            except Exception as e:
                # Set exception on all futures
                for text, future in batch:
                    future.set_exception(e)

    async def _batch_generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for a batch of texts"""
        # In production, this would call OpenAI or local model
        # For now, return mock embeddings
        embeddings = []
        for text in texts:
            hash_val = hashlib.md5(text.encode()).hexdigest()
            np.random.seed(int(hash_val[:8], 16))
            embeddings.append(np.random.randn(1536))
        return embeddings


class ConnectionPool:
    """Manage database connection pooling"""

    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections = asyncio.Queue(maxsize=max_connections)
        self.created_connections = 0

    async def get_connection(self):
        """Get a connection from the pool"""
        if self.connections.empty() and self.created_connections < self.max_connections:
            # Create new connection
            conn = await self._create_connection()
            self.created_connections += 1
            return conn

        # Wait for available connection
        return await self.connections.get()

    async def return_connection(self, conn):
        """Return a connection to the pool"""
        await self.connections.put(conn)

    async def _create_connection(self):
        """Create a new database connection"""
        # In production, this would create actual DB connection
        # For now, return mock connection
        return {"id": self.created_connections, "created": time.time()}


class QueryOptimizer:
    """Optimize search queries for better performance"""

    def __init__(self):
        self.query_cache = {}
        self.query_patterns = {}

    def optimize_query(self, query: str) -> str:
        """Optimize a search query"""
        # Remove extra whitespace
        query = ' '.join(query.split())

        # Convert to lowercase for consistency
        query_lower = query.lower()

        # Remove common stop words for vector search
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = query_lower.split()
        filtered_words = [w for w in words if w not in stop_words or len(words) <= 3]

        # Keep original query if too much was filtered
        if len(filtered_words) < len(words) * 0.5:
            return query

        return ' '.join(filtered_words)

    def analyze_query_pattern(self, query: str) -> Dict[str, Any]:
        """Analyze query pattern for optimization hints"""
        return {
            "is_phrase": '"' in query,
            "has_operators": any(op in query for op in ['AND', 'OR', 'NOT']),
            "word_count": len(query.split()),
            "estimated_complexity": self._estimate_complexity(query)
        }

    def _estimate_complexity(self, query: str) -> str:
        """Estimate query complexity"""
        word_count = len(query.split())
        if word_count <= 3:
            return "simple"
        elif word_count <= 10:
            return "moderate"
        else:
            return "complex"


class IndexOptimizer:
    """Optimize search indices for better performance"""

    def __init__(self):
        self.index_stats = {}
        self.last_optimization = None

    async def optimize_vector_index(self, index_name: str):
        """Optimize vector index (HNSW parameters)"""
        logger.info(f"Optimizing vector index: {index_name}")

        # In production, this would adjust HNSW parameters
        # For now, track optimization
        self.index_stats[index_name] = {
            "optimized_at": datetime.utcnow(),
            "ef_construction": 200,
            "m": 16,
            "ef_search": 50
        }

        self.last_optimization = datetime.utcnow()

    async def analyze_index_performance(self, index_name: str) -> Dict[str, Any]:
        """Analyze index performance metrics"""
        return {
            "index_name": index_name,
            "last_optimization": self.last_optimization.isoformat() if self.last_optimization else None,
            "recommended_actions": self._get_optimization_recommendations(index_name)
        }

    def _get_optimization_recommendations(self, index_name: str) -> List[str]:
        """Get optimization recommendations for an index"""
        recommendations = []

        # Check if optimization is needed
        if not self.last_optimization or (datetime.utcnow() - self.last_optimization) > timedelta(days=7):
            recommendations.append("Consider re-optimizing the index")

        # Add other recommendations based on usage patterns
        recommendations.append("Monitor query latency during peak hours")
        recommendations.append("Consider increasing ef_search for better recall")

        return recommendations


class ConcurrentSearchManager:
    """Manage concurrent search requests efficiently"""

    def __init__(self, max_concurrent: int = 50):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_searches = 0
        self.queue = asyncio.Queue()

    async def execute_search(self, search_func, *args, **kwargs):
        """Execute a search with concurrency control"""
        async with self.semaphore:
            self.active_searches += 1
            try:
                result = await search_func(*args, **kwargs)
                return result
            finally:
                self.active_searches -= 1

    def get_status(self) -> Dict[str, Any]:
        """Get concurrent search status"""
        return {
            "active_searches": self.active_searches,
            "max_concurrent": self.semaphore._initial_value,
            "queued": self.queue.qsize()
        }


# Decorators for performance optimization
def cached_result(ttl: int = 300):
    """Decorator to cache function results"""
    def decorator(func):
        cache = {}

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = hashlib.md5(
                f"{args}{kwargs}".encode()
            ).hexdigest()

            # Check cache
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < ttl:
                    return result

            # Execute function
            result = await func(*args, **kwargs)

            # Update cache
            cache[key] = (result, time.time())

            return result

        return wrapper
    return decorator


def measure_performance(func):
    """Decorator to measure function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} took {duration:.3f} seconds")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f} seconds: {e}")
            raise

    return wrapper


class PerformanceOptimizer:
    """Main performance optimization manager"""

    def __init__(self):
        self.metrics = PerformanceMetrics()
        self.cache = RedisCache()
        self.batch_processor = BatchProcessor()
        self.connection_pool = ConnectionPool()
        self.query_optimizer = QueryOptimizer()
        self.index_optimizer = IndexOptimizer()
        self.concurrent_manager = ConcurrentSearchManager()

    async def initialize(self):
        """Initialize performance optimization components"""
        await self.cache.connect()
        logger.info("Performance optimizer initialized")

    async def shutdown(self):
        """Shutdown performance optimization components"""
        await self.cache.disconnect()
        logger.info("Performance optimizer shut down")

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        return {
            "metrics": self.metrics.get_statistics(),
            "concurrent_searches": self.concurrent_manager.get_status(),
            "cache_status": {
                "connected": self.cache.client is not None,
                "ttl": self.cache.ttl
            },
            "connection_pool": {
                "max_connections": self.connection_pool.max_connections,
                "created": self.connection_pool.created_connections
            },
            "timestamp": datetime.utcnow().isoformat()
        }


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()
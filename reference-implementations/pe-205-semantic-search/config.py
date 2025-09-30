"""
Configuration Module for Semantic Search API (PE-205)
Centralized configuration management
"""

import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class SearchConfig(BaseSettings):
    """Configuration for semantic search service"""

    # API Configuration
    api_title: str = Field("Semantic Search API", description="API title")
    api_version: str = Field("1.0.0", description="API version")
    api_host: str = Field("0.0.0.0", description="API host")
    api_port: int = Field(8000, description="API port")
    api_docs_url: str = Field("/api/docs", description="API docs URL")

    # Database Configuration
    database_url: str = Field(
        "postgresql://localhost/plasma",
        description="PostgreSQL connection URL"
    )
    redis_url: str = Field(
        "redis://localhost:6379",
        description="Redis connection URL"
    )
    neo4j_uri: str = Field(
        "bolt://localhost:7687",
        description="Neo4j connection URI"
    )
    neo4j_user: str = Field("neo4j", description="Neo4j username")
    neo4j_password: str = Field("password", description="Neo4j password")

    # Embedding Configuration
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    embedding_model: str = Field(
        "text-embedding-3-large",
        description="OpenAI embedding model"
    )
    embedding_dimensions: int = Field(1536, description="Embedding dimensions")
    local_embedding_model: str = Field(
        "all-MiniLM-L6-v2",
        description="Local embedding model fallback"
    )
    use_local_embeddings: bool = Field(
        False,
        description="Use local embeddings instead of OpenAI"
    )

    # Search Configuration
    default_search_mode: str = Field("hybrid", description="Default search mode")
    default_limit: int = Field(10, description="Default result limit")
    max_limit: int = Field(100, description="Maximum result limit")
    similarity_threshold: float = Field(
        0.5,
        description="Minimum similarity threshold"
    )
    mmr_lambda: float = Field(
        0.7,
        description="MMR lambda parameter for diversity"
    )
    enable_query_expansion: bool = Field(
        True,
        description="Enable query expansion by default"
    )

    # BM25 Configuration
    bm25_k1: float = Field(1.5, description="BM25 k1 parameter")
    bm25_b: float = Field(0.75, description="BM25 b parameter")
    bm25_weight: float = Field(0.3, description="BM25 weight in hybrid search")
    vector_weight: float = Field(0.7, description="Vector weight in hybrid search")

    # Document Processing
    max_chunk_size: int = Field(
        1000,
        description="Maximum chunk size in tokens"
    )
    chunk_overlap: int = Field(
        200,
        description="Chunk overlap in tokens"
    )
    min_chunk_size: int = Field(
        100,
        description="Minimum chunk size in tokens"
    )

    # Caching Configuration
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")
    embedding_cache_ttl: int = Field(
        7200,
        description="Embedding cache TTL in seconds"
    )
    result_cache_ttl: int = Field(
        1800,
        description="Search result cache TTL in seconds"
    )
    enable_caching: bool = Field(True, description="Enable caching")

    # Performance Configuration
    batch_size: int = Field(100, description="Batch processing size")
    max_concurrent_requests: int = Field(
        50,
        description="Maximum concurrent requests"
    )
    connection_pool_size: int = Field(
        10,
        description="Database connection pool size"
    )
    request_timeout: int = Field(
        30,
        description="Request timeout in seconds"
    )

    # Index Configuration
    index_type: str = Field("HNSW", description="Vector index type")
    hnsw_ef_construction: int = Field(
        200,
        description="HNSW ef_construction parameter"
    )
    hnsw_m: int = Field(16, description="HNSW M parameter")
    hnsw_ef_search: int = Field(50, description="HNSW ef_search parameter")

    # Monitoring Configuration
    enable_metrics: bool = Field(True, description="Enable metrics collection")
    metrics_port: int = Field(9090, description="Metrics port")
    log_level: str = Field("INFO", description="Logging level")
    log_format: str = Field("json", description="Log format (json or text)")

    # Security Configuration
    api_key_header: str = Field(
        "X-API-Key",
        description="API key header name"
    )
    require_api_key: bool = Field(
        False,
        description="Require API key for requests"
    )
    cors_origins: str = Field("*", description="CORS allowed origins")
    rate_limit_per_minute: int = Field(
        100,
        description="Rate limit per minute per client"
    )

    @validator("bm25_weight", "vector_weight")
    def validate_weights(cls, v, values):
        """Ensure search weights sum to 1.0"""
        if "bm25_weight" in values and "vector_weight" in values:
            if abs(values["bm25_weight"] + values["vector_weight"] - 1.0) > 0.001:
                raise ValueError("BM25 and vector weights must sum to 1.0")
        return v

    @validator("similarity_threshold")
    def validate_threshold(cls, v):
        """Ensure similarity threshold is between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError("Similarity threshold must be between 0 and 1")
        return v

    @validator("mmr_lambda")
    def validate_mmr_lambda(cls, v):
        """Ensure MMR lambda is between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError("MMR lambda must be between 0 and 1")
        return v

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class ProductionConfig(SearchConfig):
    """Production configuration with stricter settings"""

    # Override defaults for production
    require_api_key: bool = True
    enable_metrics: bool = True
    log_level: str = "WARNING"
    cors_origins: str = "https://api.plasma-engine.com"
    rate_limit_per_minute: int = 60

    # Production database settings
    connection_pool_size: int = 20
    max_concurrent_requests: int = 100

    # Production cache settings
    cache_ttl: int = 7200
    embedding_cache_ttl: int = 86400


class DevelopmentConfig(SearchConfig):
    """Development configuration with debugging enabled"""

    # Override defaults for development
    log_level: str = "DEBUG"
    log_format: str = "text"
    require_api_key: bool = False
    cors_origins: str = "*"

    # Development settings
    enable_metrics: bool = True
    connection_pool_size: int = 5
    max_concurrent_requests: int = 10


class TestConfig(SearchConfig):
    """Test configuration for unit tests"""

    # Override for testing
    database_url: str = "sqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/15"
    use_local_embeddings: bool = True
    require_api_key: bool = False

    # Test settings
    cache_ttl: int = 60
    batch_size: int = 10
    max_concurrent_requests: int = 5


def get_config(env: str = None) -> SearchConfig:
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv("ENVIRONMENT", "development")

    configs = {
        "production": ProductionConfig,
        "development": DevelopmentConfig,
        "test": TestConfig
    }

    config_class = configs.get(env.lower(), DevelopmentConfig)
    return config_class()


# Global configuration instance
config = get_config()


def get_database_settings() -> Dict[str, Any]:
    """Get database configuration as dictionary"""
    return {
        "database_url": config.database_url,
        "pool_size": config.connection_pool_size,
        "echo": config.log_level == "DEBUG"
    }


def get_redis_settings() -> Dict[str, Any]:
    """Get Redis configuration as dictionary"""
    return {
        "url": config.redis_url,
        "encoding": "utf-8",
        "decode_responses": True
    }


def get_neo4j_settings() -> Dict[str, Any]:
    """Get Neo4j configuration as dictionary"""
    return {
        "uri": config.neo4j_uri,
        "auth": (config.neo4j_user, config.neo4j_password)
    }


def get_embedding_settings() -> Dict[str, Any]:
    """Get embedding configuration as dictionary"""
    return {
        "model": config.embedding_model,
        "dimensions": config.embedding_dimensions,
        "use_local": config.use_local_embeddings,
        "local_model": config.local_embedding_model,
        "api_key": config.openai_api_key
    }


def get_search_settings() -> Dict[str, Any]:
    """Get search configuration as dictionary"""
    return {
        "default_mode": config.default_search_mode,
        "default_limit": config.default_limit,
        "max_limit": config.max_limit,
        "similarity_threshold": config.similarity_threshold,
        "mmr_lambda": config.mmr_lambda,
        "enable_query_expansion": config.enable_query_expansion,
        "bm25_weight": config.bm25_weight,
        "vector_weight": config.vector_weight
    }


def get_performance_settings() -> Dict[str, Any]:
    """Get performance configuration as dictionary"""
    return {
        "batch_size": config.batch_size,
        "max_concurrent": config.max_concurrent_requests,
        "cache_ttl": config.cache_ttl,
        "enable_caching": config.enable_caching,
        "request_timeout": config.request_timeout
    }


# Export configuration
__all__ = [
    "config",
    "get_config",
    "SearchConfig",
    "ProductionConfig",
    "DevelopmentConfig",
    "TestConfig",
    "get_database_settings",
    "get_redis_settings",
    "get_neo4j_settings",
    "get_embedding_settings",
    "get_search_settings",
    "get_performance_settings"
]
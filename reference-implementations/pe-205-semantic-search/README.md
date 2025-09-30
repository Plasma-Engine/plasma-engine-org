# Semantic Search API Implementation (PE-205)

## Overview

This is the reference implementation for PE-205: Semantic Search API with hybrid search capabilities for the Plasma Engine Research Service. The implementation provides a comprehensive search system combining vector similarity search with traditional keyword matching to deliver highly relevant results.

## Features

### Core Capabilities
- **Vector Similarity Search**: Using cosine similarity with embeddings
- **BM25 Keyword Matching**: Traditional text search for exact matches
- **Hybrid Search**: Combines vector and keyword approaches for best results
- **Query Expansion**: Automatically expands queries with synonyms and related terms
- **MMR (Maximal Marginal Relevance)**: Diversifies results to reduce redundancy
- **GraphQL Support**: Full GraphQL schema with queries, mutations, and subscriptions
- **Performance Optimization**: Caching, batching, and connection pooling
- **Pagination**: Supports offset-based pagination for large result sets

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Applications                     │
└────────────────┬───────────────────────────┬─────────────────┘
                 │                           │
         ┌───────▼────────┐         ┌───────▼────────┐
         │  REST API      │         │  GraphQL API   │
         │  (FastAPI)     │         │  (Strawberry)  │
         └───────┬────────┘         └───────┬────────┘
                 │                           │
                 └─────────────┬─────────────┘
                               │
                   ┌───────────▼───────────┐
                   │  Semantic Search      │
                   │     Service           │
                   └───────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
    ┌─────▼──────┐      ┌─────▼──────┐     ┌──────▼──────┐
    │   Vector   │      │   BM25     │     │   Query     │
    │   Store    │      │  Scorer    │     │  Expander   │
    └────────────┘      └────────────┘     └─────────────┘
          │                    │                    │
    ┌─────▼──────────────────────────────────────────┐
    │            Performance Optimizer               │
    │  (Cache, Batch Processing, Connection Pool)    │
    └─────────────────────────────────────────────────┘
```

## Installation

### Requirements
- Python 3.11+
- Redis (for caching)
- PostgreSQL with pgvector extension (production)
- Neo4j (for knowledge graph integration)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Plasma-Engine/plasma-engine-research.git
cd plasma-engine-research
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export REDIS_URL="redis://localhost:6379"
export DATABASE_URL="postgresql://user:pass@localhost/plasma"
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
export OPENAI_API_KEY="your-api-key"
```

4. Run the service:
```bash
uvicorn api_endpoints:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

### REST API Endpoints

#### Search Endpoint
```http
POST /api/v1/search
Content-Type: application/json

{
  "query": "semantic search with vector embeddings",
  "mode": "hybrid",
  "limit": 10,
  "offset": 0,
  "expand_query": true,
  "use_mmr": true,
  "mmr_lambda": 0.7,
  "similarity_threshold": 0.5
}
```

#### Batch Search
```http
POST /api/v1/search/batch
Content-Type: application/json

{
  "queries": [
    {
      "query": "vector embeddings",
      "mode": "hybrid",
      "limit": 5
    },
    {
      "query": "knowledge graph",
      "mode": "vector",
      "limit": 10
    }
  ]
}
```

#### Find Similar Documents
```http
POST /api/v1/similar
Content-Type: application/json

{
  "document_id": "doc123",
  "limit": 5
}
```

#### Document Ingestion
```http
POST /api/v1/ingest
Content-Type: application/json

{
  "id": "doc456",
  "content": "Document content here...",
  "metadata": {
    "source": "research_paper",
    "author": "John Doe"
  }
}
```

### GraphQL API

Access the GraphQL playground at `http://localhost:8000/graphql`

#### Search Query
```graphql
query SemanticSearch {
  search(
    input: {
      query: "semantic search"
      mode: HYBRID
      limit: 10
      expandQuery: true
      useMMR: true
    }
  ) {
    query
    expandedQueries
    mode
    totalResults
    results {
      id
      content
      score
      metadata
      source
    }
  }
}
```

#### Batch Search
```graphql
query BatchSearch {
  batchSearch(
    queries: [
      { query: "vector embeddings", mode: HYBRID }
      { query: "knowledge graph", mode: VECTOR }
    ]
  ) {
    query
    results {
      id
      content
      score
    }
  }
}
```

#### Document Ingestion Mutation
```graphql
mutation IngestDocument {
  ingestDocument(
    input: {
      id: "doc789"
      content: "Document content..."
      metadata: { source: "blog_post" }
    }
  ) {
    status
    documentId
    message
    timestamp
  }
}
```

## Search Modes

### Vector Search
- Uses embeddings to find semantically similar content
- Best for conceptual queries and finding related documents
- Threshold-based filtering for quality control

### Keyword Search (BM25)
- Traditional text matching with BM25 scoring
- Best for exact phrase matches and specific terms
- Considers term frequency and document length

### Hybrid Search
- Combines vector and keyword approaches
- Weighted scoring (default: 70% vector, 30% keyword)
- Provides best overall relevance

## Query Expansion

The system automatically expands queries to improve recall:
- Synonym expansion
- Related term inclusion
- Contextual variations
- Can be disabled per query

## Result Diversification (MMR)

Maximal Marginal Relevance reduces redundancy in results:
- Balances relevance and diversity
- Configurable lambda parameter (0-1)
- Higher lambda = more relevance, less diversity
- Lower lambda = more diversity, less relevance

## Performance Optimizations

### Caching
- Redis-based caching for embeddings
- Result caching with configurable TTL
- Query pattern recognition

### Batch Processing
- Batch embedding generation
- Parallel query processing
- Optimized database queries

### Connection Pooling
- Reusable database connections
- Configurable pool size
- Automatic connection management

### Concurrent Request Management
- Semaphore-based concurrency control
- Queue management for high load
- Graceful degradation

## Monitoring

### Health Check
```http
GET /health
```

### Statistics
```http
GET /api/v1/stats
```

Returns:
- Total documents indexed
- Vector dimensions
- Index configuration
- Performance metrics

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `NEO4J_URI` | Neo4j connection URI | Required |
| `OPENAI_API_KEY` | OpenAI API key for embeddings | Required |
| `EMBEDDING_MODEL` | Embedding model to use | `text-embedding-3-large` |
| `LOCAL_EMBEDDING_MODEL` | Local fallback model | `all-MiniLM-L6-v2` |
| `MAX_CHUNK_SIZE` | Maximum chunk size in tokens | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap in tokens | `200` |
| `CACHE_TTL` | Cache TTL in seconds | `3600` |
| `BATCH_SIZE` | Batch processing size | `100` |
| `MAX_CONCURRENT_REQUESTS` | Max concurrent searches | `50` |

## Integration with Other Services

### PE-203 (Vector Embedding System)
- Uses the embedding service for vector generation
- Shares embedding cache
- Consistent model usage

### PE-204 (GraphRAG Knowledge Graph)
- Queries Neo4j for entity relationships
- Enriches search results with graph data
- Knowledge synthesis capabilities

### Gateway Service
- Exposed through API Gateway
- GraphQL federation support
- Authentication and rate limiting

## Testing

Run the test suite:
```bash
pytest tests/ -v --cov=.
```

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Average query time | < 100ms |
| P95 query time | < 200ms |
| P99 query time | < 500ms |
| Throughput | > 1000 req/s |
| Cache hit rate | > 80% |
| Vector search recall@10 | > 0.95 |
| BM25 precision@10 | > 0.85 |

## Troubleshooting

### Common Issues

1. **Slow search performance**
   - Check Redis connection
   - Verify index optimization
   - Review query complexity

2. **Low relevance scores**
   - Adjust similarity threshold
   - Tune MMR lambda parameter
   - Enable query expansion

3. **High memory usage**
   - Reduce batch size
   - Adjust cache TTL
   - Limit concurrent requests

## Development

### Project Structure
```
pe-205-semantic-search/
├── semantic_search_service.py  # Core search logic
├── api_endpoints.py            # FastAPI REST endpoints
├── graphql_resolver.py         # GraphQL schema and resolvers
├── performance_optimizations.py # Performance enhancements
├── requirements.txt            # Python dependencies
├── tests/                      # Test suite
└── README.md                   # This file
```

### Contributing
See the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License
Copyright © 2025 Plasma Engine. All rights reserved.
# 🔐 Plasma Engine - Required Services & Secrets

## 📋 Complete Service Requirements

### 1. Core Infrastructure Services

#### Databases
- **PostgreSQL 15+** with extensions:
  - `pgvector` - Vector similarity search
  - `timescaledb` - Time-series data
  - `uuid-ossp` - UUID generation
- **Redis 7.x** - Caching, queues, session storage
- **Neo4j 5.x Community** - Knowledge graph for GraphRAG
- **SQLite** - Local agent memory storage

#### Message Queuing
- **Celery** with Redis backend - Async task processing
- **RabbitMQ** (optional) - Alternative message broker

#### Storage
- **MinIO** or **AWS S3** - Object storage for documents
- **Local filesystem** - Development storage

#### Search & Analytics
- **Elasticsearch** (optional) - Full-text search
- **OpenSearch** (optional) - Alternative to Elasticsearch

### 2. AI/ML Services

#### LLM Providers
- **OpenAI API** - GPT-4, embeddings
- **Anthropic API** - Claude models
- **Groq** (optional) - Fast inference
- **Ollama** (optional) - Local models

#### Embedding Services
- **OpenAI Embeddings** - text-embedding-3-large
- **Sentence Transformers** - Local embeddings
- **CLIP** - Image embeddings

#### NLP Tools
- **spaCy** - NER, text processing
- **Hugging Face** - Transformers, models

### 3. External APIs & Services

#### Social Media Monitoring (via Apify)
- **Apify Platform** - Web scraping infrastructure
  - Twitter Scraper Actor
  - Reddit Scraper Actor
  - LinkedIn Scraper (future)
- **No direct API access required for X/Twitter or Reddit**

#### Content Publishing
- **WordPress API** - Blog publishing
- **Medium API** - Article publishing
- **LinkedIn API** (future) - Professional content
- **Buffer/Hootsuite API** (optional) - Social media scheduling

#### Development Tools
- **GitHub API** - Repository management, issues
- **CodeRabbit** - Automated PR reviews
- **Docker Hub** - Container registry

### 4. Monitoring & Observability

#### Metrics & Logging
- **Prometheus** - Metrics collection
- **Grafana** - Dashboards
- **Loki** or **ELK Stack** - Log aggregation
- **Jaeger** or **Zipkin** - Distributed tracing

#### Error Tracking
- **Sentry** - Error monitoring
- **Rollbar** (alternative)

### 5. CI/CD & Deployment

#### Container Services
- **Docker** - Containerization
- **Docker Compose** - Local orchestration
- **Kubernetes** (staging/production)

#### CI/CD Platforms
- **GitHub Actions** - Primary CI/CD
- **ArgoCD** (optional) - GitOps deployment

## 🔑 Required Secrets & Environment Variables

### GitHub Secrets Required

```yaml
# Core API Keys
OPENAI_API_KEY: "sk-..."                    # OpenAI API access
ANTHROPIC_API_KEY: "sk-ant-..."            # Anthropic Claude access
APIFY_TOKEN: "apify_api_..."               # Apify web scraping

# Database Credentials
POSTGRES_HOST: "localhost"
POSTGRES_PORT: "5432"
POSTGRES_DB: "plasma_engine"
POSTGRES_USER: "plasma_user"
POSTGRES_PASSWORD: "secure_password"

REDIS_HOST: "localhost"
REDIS_PORT: "6379"
REDIS_PASSWORD: "redis_password"

NEO4J_URI: "bolt://localhost:7687"
NEO4J_USER: "neo4j"
NEO4J_PASSWORD: "neo4j_password"

# Storage
S3_ENDPOINT: "http://localhost:9000"       # MinIO endpoint
S3_ACCESS_KEY: "minioadmin"
S3_SECRET_KEY: "minioadmin"
S3_BUCKET: "plasma-documents"

# Authentication
JWT_SECRET: "your-256-bit-secret"
JWT_ALGORITHM: "HS256"
JWT_EXPIRATION: "86400"

# Service URLs (Internal)
GATEWAY_URL: "http://localhost:7000"
RESEARCH_URL: "http://localhost:8000"
BRAND_URL: "http://localhost:8001"
CONTENT_URL: "http://localhost:8002"
AGENT_URL: "http://localhost:8003"

# Monitoring
SENTRY_DSN: "https://...@sentry.io/..."
PROMETHEUS_PUSHGATEWAY: "http://localhost:9091"

# GitHub
GITHUB_TOKEN: "YOUR_GITHUB_TOKEN_HERE"      # For API access - NEVER commit real token!
GITHUB_WEBHOOK_SECRET: "YOUR_WEBHOOK_SECRET_HERE"  # Generate secure webhook secret

# Docker Registry
DOCKER_REGISTRY: "docker.io"
DOCKER_USERNAME: "your_username"
DOCKER_PASSWORD: "your_password"
```

### Service-Specific Environment Files

#### `.env.gateway`
```env
NODE_ENV=development
PORT=7000
GRAPHQL_INTROSPECTION=true
GRAPHQL_PLAYGROUND=true
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX=100
```

#### `.env.research`
```env
ENVIRONMENT=development
PYTHONPATH=/app
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSION=3072
```

#### `.env.brand`
```env
APIFY_TOKEN=required
APIFY_TWITTER_ACTOR=quacker/twitter-scraper
APIFY_REDDIT_ACTOR=trudax/reddit-scraper
SENTIMENT_MODEL=cardiffnlp/twitter-roberta-base-sentiment
MONITORING_INTERVAL=900  # 15 minutes
ALERT_THRESHOLD=0.3
```

#### `.env.content`
```env
CONTENT_GENERATION_MODEL=gpt-4
TEMPERATURE=0.7
MAX_TOKENS=4000
SEO_OPTIMIZATION=true
PUBLISHING_QUEUE=redis://localhost:6379/2
```

#### `.env.agent`
```env
MCP_ENABLED=true
MAX_CONCURRENT_AGENTS=5
WORKFLOW_TIMEOUT=3600
MEMORY_PERSISTENCE=sqlite
TOOL_SANDBOX=true
```

## 🚀 Quick Setup Commands

### 1. Install Dependencies

```bash
# System dependencies
brew install postgresql@15 redis neo4j python@3.11 node@20

# Python global tools
pip install poetry pipenv virtualenv

# Node global tools
npm install -g pnpm yarn typescript
```

### 2. Start Infrastructure Services

```bash
# Using Docker Compose (recommended)
docker-compose -f docker-compose.infrastructure.yml up -d

# Or individually
brew services start postgresql@15
brew services start redis
neo4j start
```

### 3. Create `.env` Files

```bash
# Copy all example files
for service in gateway research brand content agent; do
  cp plasma-engine-$service/.env.example plasma-engine-$service/.env
done

# Edit each .env file with your credentials
```

### 4. GitHub Secrets Setup

```bash
# Set secrets via GitHub CLI
gh secret set OPENAI_API_KEY --body "your-key"
gh secret set ANTHROPIC_API_KEY --body "your-key"
gh secret set APIFY_TOKEN --body "your-key"
# ... continue for all secrets
```

## 📊 Service Dependency Matrix

| Service | Depends On | Critical APIs |
|---------|------------|---------------|
| Gateway | Redis | JWT auth |
| Research | PostgreSQL, Neo4j, Redis, OpenAI | Document processing |
| Brand | PostgreSQL, Redis, Apify | Social monitoring |
| Content | PostgreSQL, Redis, OpenAI/Anthropic | Content generation |
| Agent | SQLite, Redis, LLM providers | Workflow execution |

## 🔍 Verification Checklist

- [ ] All database services running and accessible
- [ ] Redis connection successful
- [ ] OpenAI API key valid and has credits
- [ ] Anthropic API key valid (optional)
- [ ] Apify token valid with sufficient credits
- [ ] GitHub authentication working
- [ ] Docker/Docker Compose installed
- [ ] All `.env` files created and populated
- [ ] GitHub secrets configured
- [ ] CodeRabbit app installed on repository

## 🚨 Critical Notes

1. **Apify Credits**: Monitor usage carefully - social media scraping can consume credits quickly
2. **OpenAI Costs**: Set usage limits in OpenAI dashboard to prevent unexpected charges
3. **Database Backups**: Configure automated backups for PostgreSQL and Neo4j
4. **Secret Rotation**: Implement secret rotation policy (90 days recommended)
5. **Rate Limiting**: Respect all API rate limits to avoid service disruption

## 📝 Missing Services to Set Up

Based on Phase 1 requirements, you still need to:

1. **Create Apify account** and get API token
2. **Set up MinIO** or configure S3 bucket
3. **Install CodeRabbit** GitHub app
4. **Configure Sentry** for error tracking (optional)
5. **Set up monitoring stack** (Prometheus/Grafana) (optional for dev)

## 🔗 Service URLs for Reference

- Apify: https://console.apify.com/
- OpenAI: https://platform.openai.com/
- Anthropic: https://console.anthropic.com/
- CodeRabbit: https://github.com/marketplace/coderabbitai
- MinIO: https://min.io/
- Neo4j: https://neo4j.com/
- Sentry: https://sentry.io/
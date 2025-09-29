#!/bin/bash
# Automated GitHub Issue Generation for Phase 1
# This script creates all 62 Phase 1 issues across Plasma Engine repositories

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Plasma Engine Phase 1 Issue Generation ===${NC}"
echo "Creating 62 GitHub issues across all service repositories"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Function to create an issue
create_issue() {
    local repo=$1
    local title=$2
    local body=$3
    local labels=$4
    local priority=$5

    echo -e "${YELLOW}Creating: ${title}${NC}"

    gh issue create \
        --repo "Plasma-Engine/${repo}" \
        --title "${title}" \
        --body "${body}" \
        --label "${labels},${priority},phase-1,cursor-ready" \
        2>&1 | grep -E "http" || echo -e "${RED}Failed to create issue${NC}"
}

# Gateway Service Issues (10 tickets)
echo -e "${GREEN}=== Creating Gateway Service Issues ===${NC}"

create_issue "plasma-engine-gateway" \
    "[Gateway-Task] Set up TypeScript project structure (PE-101)" \
    "## Description
Set up FastAPI project structure with TypeScript, Apollo Server, and proper configuration.

## Acceptance Criteria
- [ ] TypeScript application scaffolded with proper structure
- [ ] npm dependencies configured
- [ ] Docker setup with multi-stage build
- [ ] Health check endpoint implemented
- [ ] OpenAPI documentation enabled

## Technical Details
- Use Node.js 20+ with TypeScript 5.x
- Implement /health, /ready, /metrics endpoints
- Structure: src/api/v1/, src/core/, src/models/
- Environment-based configuration

## Dependencies
- Requires: PE-03 (CI/CD workflows)

## Story Points: 3
## Sprint: 1" \
    "gateway,task" \
    "P0-critical"

create_issue "plasma-engine-gateway" \
    "[Gateway-Feature] Implement JWT authentication middleware (PE-102)" \
    "## Description
Implement JWT token generation, validation, and authentication middleware.

## Acceptance Criteria
- [ ] JWT token generation and validation
- [ ] Refresh token mechanism
- [ ] Auth0/Clerk integration
- [ ] Rate limiting per user
- [ ] Session management with Redis

## Technical Details
- RS256 algorithm for JWT signing
- 15min access token, 7 day refresh token
- Redis for token blacklisting
- Implement OAuth2 password flow
- Support API key authentication

## Dependencies
- Requires: PE-101
- Blocks: All authenticated endpoints

## Story Points: 5
## Sprint: 1" \
    "gateway,feature" \
    "P0-critical"

create_issue "plasma-engine-gateway" \
    "[Gateway-Feature] Set up GraphQL federation gateway (PE-103)" \
    "## Description
Create GraphQL federation layer with Apollo Gateway.

## Acceptance Criteria
- [ ] Apollo Server configured
- [ ] Federation gateway setup
- [ ] Service discovery mechanism
- [ ] Schema stitching for subgraphs
- [ ] Query planning optimization

## Technical Details
- Apollo Gateway v2 with @apollo/subgraph
- Service registry in Redis
- Health checks for subgraphs
- Query complexity analysis
- DataLoader for N+1 prevention

## Dependencies
- Requires: PE-102
- Blocks: PE-201, PE-301, PE-401, PE-501

## Story Points: 8
## Sprint: 2" \
    "gateway,feature" \
    "P0-critical"

create_issue "plasma-engine-gateway" \
    "[Gateway-Feature] Implement request validation and sanitization (PE-104)" \
    "## Description
Implement request validation, sanitization, and RBAC authorization.

## Acceptance Criteria
- [ ] Request validation and sanitization
- [ ] Response formatting
- [ ] Field-level permissions
- [ ] Data masking for PII
- [ ] Compression support

## Dependencies
- Requires: PE-103

## Story Points: 5
## Sprint: 2" \
    "gateway,feature" \
    "P1-high"

create_issue "plasma-engine-gateway" \
    "[Gateway-Feature] Implement rate limiting and throttling (PE-106)" \
    "## Description
Implement rate limiting and throttling for API endpoints.

## Acceptance Criteria
- [ ] Per-user rate limits
- [ ] Per-IP rate limits
- [ ] Tiered limits by plan
- [ ] Redis-backed counters
- [ ] Graceful limit responses

## Technical Details
- Token bucket algorithm
- Sliding window counters
- Rate limit headers (X-RateLimit-*)

## Story Points: 3
## Sprint: 3" \
    "gateway,feature" \
    "P1-high"

# Research Service Issues (10 tickets)
echo -e "${GREEN}=== Creating Research Service Issues ===${NC}"

create_issue "plasma-engine-research" \
    "[Research-Task] Set up Python service with async support (PE-201)" \
    "## Description
Set up Python FastAPI service with async support and Celery workers.

## Acceptance Criteria
- [ ] FastAPI application structure
- [ ] Async/await patterns
- [ ] Celery worker setup
- [ ] Redis queue configuration
- [ ] Docker containerization

## Technical Details
- Python 3.11+ with asyncio
- Celery 5.3+ with Redis backend
- SQLAlchemy 2.0 with async support

## Story Points: 3
## Sprint: 1" \
    "research,task" \
    "P0-critical"

create_issue "plasma-engine-research" \
    "[Research-Feature] Implement document ingestion pipeline (PE-202)" \
    "## Description
Create document ingestion pipeline supporting multiple formats.

## Acceptance Criteria
- [ ] Multi-format support (PDF, DOCX, MD, HTML)
- [ ] Chunking strategies
- [ ] Metadata extraction
- [ ] S3/MinIO storage
- [ ] Async processing queue

## Technical Details
- Unstructured.io for parsing
- Sliding window chunking (1000 tokens, 200 overlap)
- Apache Tika for metadata

## Dependencies
- Requires: PE-201
- Blocks: PE-203

## Story Points: 8
## Sprint: 2" \
    "research,feature" \
    "P0-critical"

create_issue "plasma-engine-research" \
    "[Research-Feature] Create vector embedding system (PE-203)" \
    "## Description
Implement vector embedding system with OpenAI and local models.

## Acceptance Criteria
- [ ] OpenAI embeddings integration
- [ ] Local embedding option (Sentence-Transformers)
- [ ] pgvector database setup
- [ ] Batch processing optimization
- [ ] Embedding cache layer

## Technical Details
- text-embedding-3-large (3072 dimensions)
- all-MiniLM-L6-v2 for local option
- HNSW index for similarity search

## Dependencies
- Requires: PE-202
- Blocks: PE-204

## Story Points: 5
## Sprint: 2" \
    "research,feature" \
    "P0-critical"

create_issue "plasma-engine-research" \
    "[Research-Feature] Build GraphRAG knowledge graph (PE-204)" \
    "## Description
Build GraphRAG knowledge graph with Neo4j.

## Acceptance Criteria
- [ ] Neo4j integration
- [ ] Entity extraction (NER)
- [ ] Relationship mapping
- [ ] Graph traversal queries
- [ ] Knowledge synthesis
- [ ] Citation tracking

## Technical Details
- Neo4j 5.x with APOC procedures
- spaCy for NER (en_core_web_trf)
- Cypher query optimization

## Dependencies
- Requires: PE-203

## Story Points: 13
## Sprint: 3" \
    "research,feature" \
    "P0-critical"

create_issue "plasma-engine-research" \
    "[Research-Feature] Implement semantic search API (PE-205)" \
    "## Description
Implement semantic search API with vector and hybrid search.

## Acceptance Criteria
- [ ] Vector similarity search
- [ ] Hybrid search (vector + keyword)
- [ ] Query expansion
- [ ] Result ranking
- [ ] GraphQL resolver

## Technical Details
- Cosine similarity with threshold
- BM25 for keyword matching
- Query understanding with LLM

## Dependencies
- Requires: PE-203, PE-204
- Blocked by: PE-103

## Story Points: 5
## Sprint: 3" \
    "research,feature" \
    "P0-critical"

# Brand Service Issues (10 tickets)
echo -e "${GREEN}=== Creating Brand Service Issues ===${NC}"

create_issue "plasma-engine-brand" \
    "[Brand-Task] Set up service with Celery and scheduled tasks (PE-301)" \
    "## Description
Set up Python service with Celery workers and scheduled tasks.

## Acceptance Criteria
- [ ] Python service scaffold
- [ ] Kafka/Redis Streams setup
- [ ] PostgreSQL + TimescaleDB
- [ ] Docker compose configuration
- [ ] Worker pool management

## Technical Details
- Python 3.11+ with asyncio
- Kafka 3.x or Redis Streams
- TimescaleDB for time-series data

## Story Points: 5
## Sprint: 1" \
    "brand,task" \
    "P0-critical"

create_issue "plasma-engine-brand" \
    "[Brand-Feature] Implement X/Twitter collector using Apify (PE-302)" \
    "## Description
Implement X/Twitter data collection using Apify.

## Acceptance Criteria
- [ ] X API v2 integration
- [ ] Rate limit handling
- [ ] Mention tracking
- [ ] Hashtag monitoring
- [ ] User timeline collection
- [ ] Data normalization

## Technical Details
- Tweepy 4.x for API access
- Exponential backoff for rate limits
- Streaming API for real-time

## Dependencies
- Requires: PE-301

## Story Points: 8
## Sprint: 2" \
    "brand,feature" \
    "P0-critical"

create_issue "plasma-engine-brand" \
    "[Brand-Feature] Build Reddit monitoring using Apify (PE-303)" \
    "## Description
Build Reddit monitoring system using Apify.

## Acceptance Criteria
- [ ] Reddit API integration
- [ ] Subreddit monitoring
- [ ] Comment thread tracking
- [ ] Keyword alerts
- [ ] Sentiment preprocessing

## Technical Details
- PRAW (Python Reddit API Wrapper)
- Pushshift for historical data

## Dependencies
- Requires: PE-301

## Story Points: 5
## Sprint: 2" \
    "brand,feature" \
    "P1-high"

create_issue "plasma-engine-brand" \
    "[Brand-Feature] Create sentiment analysis pipeline (PE-304)" \
    "## Description
Create sentiment analysis pipeline with transformer models.

## Acceptance Criteria
- [ ] Transformer model integration
- [ ] Multi-language support
- [ ] Aspect-based sentiment
- [ ] Emotion detection
- [ ] Batch processing

## Technical Details
- RoBERTa for sentiment (cardiffnlp/twitter-roberta-base-sentiment)
- XLM-RoBERTa for multilingual

## Dependencies
- Requires: PE-302, PE-303

## Story Points: 8
## Sprint: 3" \
    "brand,feature" \
    "P0-critical"

create_issue "plasma-engine-brand" \
    "[Brand-Feature] Implement trend detection system (PE-305)" \
    "## Description
Implement trend detection and anomaly detection system.

## Acceptance Criteria
- [ ] Time series analysis
- [ ] Anomaly detection
- [ ] Viral content identification
- [ ] Topic modeling
- [ ] Alert triggers

## Technical Details
- Prophet for time series forecasting
- Isolation Forest for anomalies

## Dependencies
- Requires: PE-304

## Story Points: 5
## Sprint: 3" \
    "brand,feature" \
    "P1-high"

# Content Service Issues (10 tickets)
echo -e "${GREEN}=== Creating Content Service Issues ===${NC}"

create_issue "plasma-engine-content" \
    "[Content-Task] Set up FastAPI with LangChain integration (PE-401)" \
    "## Description
Set up content generation service with FastAPI and LangChain.

## Acceptance Criteria
- [ ] FastAPI structure
- [ ] Celery workers
- [ ] PostgreSQL models
- [ ] S3 media storage
- [ ] Template system

## Technical Details
- Python 3.11+ with FastAPI
- Celery with Redis broker
- Jinja2 for templates

## Story Points: 3
## Sprint: 1" \
    "content,task" \
    "P0-critical"

create_issue "plasma-engine-content" \
    "[Content-Feature] Implement blog post generation (PE-402)" \
    "## Description
Implement AI-powered blog post generation.

## Acceptance Criteria
- [ ] OpenAI/Anthropic integration
- [ ] Prompt templates
- [ ] Style guide enforcement
- [ ] Token optimization
- [ ] Streaming generation

## Technical Details
- OpenAI GPT-4/Claude-3 integration
- Prompt chaining with LangChain

## Dependencies
- Requires: PE-401

## Story Points: 8
## Sprint: 2" \
    "content,feature" \
    "P0-critical"

create_issue "plasma-engine-content" \
    "[Content-Feature] Create social media content generator (PE-403)" \
    "## Description
Create brand voice system for consistent content generation.

## Acceptance Criteria
- [ ] Voice profile management
- [ ] Tone analysis
- [ ] Style consistency checks
- [ ] Custom instructions
- [ ] A/B testing variants

## Technical Details
- Voice embedding vectors
- Style transfer techniques

## Dependencies
- Requires: PE-402

## Story Points: 5
## Sprint: 2" \
    "content,feature" \
    "P1-high"

create_issue "plasma-engine-content" \
    "[Content-Feature] Build email campaign generator (PE-404)" \
    "## Description
Build content calendar and campaign management system.

## Acceptance Criteria
- [ ] Campaign management
- [ ] Scheduling system
- [ ] Approval workflow
- [ ] Version control
- [ ] Publishing queue

## Dependencies
- Requires: PE-401

## Story Points: 5
## Sprint: 3" \
    "content,feature" \
    "P1-high"

create_issue "plasma-engine-content" \
    "[Content-Feature] Implement content optimization engine (PE-405)" \
    "## Description
Implement multi-platform publishing integrations.

## Acceptance Criteria
- [ ] WordPress API
- [ ] LinkedIn posting
- [ ] X/Twitter threads
- [ ] Medium integration
- [ ] Webhook notifications

## Technical Details
- WordPress REST API v2
- LinkedIn Share API
- Twitter API v2 for threads

## Dependencies
- Requires: PE-404

## Story Points: 8
## Sprint: 3" \
    "content,feature" \
    "P0-critical"

# Agent Service Issues (10 tickets)
echo -e "${GREEN}=== Creating Agent Service Issues ===${NC}"

create_issue "plasma-engine-agent" \
    "[Agent-Task] Set up agent orchestration framework (PE-501)" \
    "## Description
Set up agent orchestration framework with Temporal/Prefect.

## Acceptance Criteria
- [ ] Python async service
- [ ] Temporal/Prefect setup
- [ ] Agent registry
- [ ] State management
- [ ] Docker configuration

## Technical Details
- Python 3.11+ with asyncio
- Temporal.io or Prefect 2.x

## Story Points: 5
## Sprint: 1" \
    "agent,task" \
    "P0-critical"

create_issue "plasma-engine-agent" \
    "[Agent-Feature] Implement browser automation agent (PE-502)" \
    "## Description
Implement browser automation with Playwright.

## Acceptance Criteria
- [ ] Playwright integration
- [ ] Headless browser pool
- [ ] Action recording
- [ ] Screenshot capture
- [ ] Form interaction

## Technical Details
- Playwright with Chrome/Firefox
- Browser pool management (5-10 instances)

## Dependencies
- Requires: PE-501

## Story Points: 8
## Sprint: 2" \
    "agent,feature" \
    "P0-critical"

create_issue "plasma-engine-agent" \
    "[Agent-Feature] Create MCP tool discovery (PE-503)" \
    "## Description
Create MCP (Model Context Protocol) tool discovery system.

## Acceptance Criteria
- [ ] MCP server integration
- [ ] Tool capability mapping
- [ ] Dynamic loading
- [ ] Permission system
- [ ] Error handling

## Technical Details
- Model Context Protocol v1.0
- Tool manifest parsing

## Dependencies
- Requires: PE-501

## Story Points: 5
## Sprint: 2" \
    "agent,feature" \
    "P1-high"

create_issue "plasma-engine-agent" \
    "[Agent-Feature] Build workflow engine (PE-504)" \
    "## Description
Build DAG-based workflow engine.

## Acceptance Criteria
- [ ] DAG execution
- [ ] Conditional logic
- [ ] Parallel execution
- [ ] Error recovery
- [ ] Checkpoint/resume
- [ ] Human-in-the-loop

## Technical Details
- Directed Acyclic Graph executor
- YAML/JSON workflow definition

## Dependencies
- Requires: PE-502, PE-503

## Story Points: 13
## Sprint: 3" \
    "agent,feature" \
    "P0-critical"

create_issue "plasma-engine-agent" \
    "[Agent-Feature] Implement LangChain agents (PE-505)" \
    "## Description
Implement LangChain-based AI agents with ReAct pattern.

## Acceptance Criteria
- [ ] ReAct agent pattern
- [ ] Tool calling
- [ ] Memory management
- [ ] Chain composition
- [ ] Prompt optimization

## Technical Details
- LangChain 0.1+ with LCEL
- ReAct with reasoning traces

## Dependencies
- Requires: PE-504

## Story Points: 8
## Sprint: 3" \
    "agent,feature" \
    "P0-critical"

# Infrastructure Issues (12 tickets)
echo -e "${GREEN}=== Creating Infrastructure Issues ===${NC}"

create_issue "plasma-engine-infra" \
    "[Infra-Task] Set up local development environment (PE-601)" \
    "## Description
Set up Docker Compose for local development environment.

## Acceptance Criteria
- [ ] Docker Compose for all services
- [ ] Hot reload configuration
- [ ] Seed data scripts
- [ ] Environment templates
- [ ] Development documentation

## Technical Details
- Docker Compose v2.x
- Service health checks
- Volume mounts for hot reload

## Story Points: 5
## Sprint: 1" \
    "infrastructure,task" \
    "P0-critical"

create_issue "plasma-engine-infra" \
    "[Infra-Task] Configure shared databases (PE-602)" \
    "## Description
Configure shared databases (PostgreSQL, Redis, Neo4j).

## Acceptance Criteria
- [ ] PostgreSQL cluster
- [ ] Redis cluster
- [ ] Neo4j setup
- [ ] TimescaleDB extension
- [ ] Backup strategies

## Technical Details
- PostgreSQL 15 with pgvector
- Redis 7.x with persistence
- Neo4j 5.x Community

## Story Points: 5
## Sprint: 1" \
    "infrastructure,task" \
    "P0-critical"

create_issue "plasma-engine-shared" \
    "[Shared-Task] Create shared Python package (PE-603)" \
    "## Description
Create shared Python package for common utilities.

## Acceptance Criteria
- [ ] Common utilities
- [ ] Database models
- [ ] Authentication helpers
- [ ] Error handling
- [ ] PyPI package setup

## Technical Details
- plasma-engine-core package
- Pydantic base models
- JWT utilities

## Story Points: 3
## Sprint: 1" \
    "shared,task" \
    "P1-high"

create_issue "plasma-engine-shared" \
    "[Shared-Task] Create shared TypeScript package (PE-604)" \
    "## Description
Create shared TypeScript package for common types and utilities.

## Acceptance Criteria
- [ ] Type definitions
- [ ] API clients
- [ ] Common components
- [ ] Utility functions
- [ ] NPM package setup

## Technical Details
- @plasma-engine/core package
- TypeScript 5.x
- Zod schemas

## Story Points: 3
## Sprint: 1" \
    "shared,task" \
    "P1-high"

create_issue "plasma-engine-infra" \
    "[Infra-Feature] Implement centralized logging (PE-605)" \
    "## Description
Implement centralized logging with Loki/ELK stack.

## Acceptance Criteria
- [ ] ELK stack or Loki
- [ ] Log aggregation
- [ ] Search interface
- [ ] Alert rules
- [ ] Retention policies

## Technical Details
- Loki + Promtail + Grafana
- Structured JSON logging

## Dependencies
- Requires: PE-601

## Story Points: 5
## Sprint: 2" \
    "infrastructure,feature" \
    "P1-high"

create_issue "plasma-engine-infra" \
    "[Infra-Feature] Set up monitoring stack (PE-606)" \
    "## Description
Set up Prometheus and Grafana monitoring stack.

## Acceptance Criteria
- [ ] Prometheus setup
- [ ] Grafana dashboards
- [ ] Service metrics
- [ ] Alert manager
- [ ] SLA tracking

## Technical Details
- Prometheus 2.x
- Grafana 10.x
- Node/container exporters

## Dependencies
- Requires: PE-601

## Story Points: 5
## Sprint: 2" \
    "infrastructure,feature" \
    "P1-high"

create_issue "plasma-engine-infra" \
    "[Infra-Task] Create staging environment (PE-607)" \
    "## Description
Create Kubernetes-based staging environment.

## Acceptance Criteria
- [ ] Kubernetes cluster
- [ ] Helm charts
- [ ] CI/CD deployment
- [ ] SSL certificates
- [ ] DNS configuration

## Technical Details
- K8s 1.28+ (EKS/GKE)
- Helm 3.x charts
- ArgoCD for GitOps

## Dependencies
- Requires: All service implementations

## Story Points: 8
## Sprint: 4" \
    "infrastructure,task" \
    "P0-critical"

create_issue "plasma-engine-infra" \
    "[Infra-Task] Implement secrets management (PE-608)" \
    "## Description
Implement secrets management with Vault or AWS Secrets Manager.

## Acceptance Criteria
- [ ] HashiCorp Vault or AWS Secrets Manager
- [ ] Rotation policies
- [ ] Service authentication
- [ ] Development secrets
- [ ] Audit logging

## Technical Details
- Vault with KV v2
- 90-day rotation
- AppRole authentication

## Dependencies
- Requires: PE-607

## Story Points: 5
## Sprint: 4" \
    "infrastructure,task" \
    "P0-critical"

create_issue "plasma-engine-infra" \
    "[Infra-Feature] Set up CI/CD pipelines (PE-609)" \
    "## Description
Set up comprehensive CI/CD pipelines with GitHub Actions.

## Acceptance Criteria
- [ ] Automated testing
- [ ] Docker builds
- [ ] Security scanning
- [ ] Deployment automation
- [ ] Rollback capability

## Technical Details
- GitHub Actions workflows
- Multi-stage Docker builds
- Trivy/Snyk scanning

## Dependencies
- Requires: PE-03

## Story Points: 8
## Sprint: 2" \
    "infrastructure,feature" \
    "P0-critical"

create_issue "plasma-engine-infra" \
    "[Infra-Task] Create disaster recovery plan (PE-611)" \
    "## Description
Create disaster recovery plan and runbooks.

## Acceptance Criteria
- [ ] Backup procedures
- [ ] Recovery runbooks
- [ ] RTO/RPO targets
- [ ] Failover testing
- [ ] Data replication

## Technical Details
- 4-hour RTO, 1-hour RPO
- Cross-region backups

## Dependencies
- Requires: PE-607

## Story Points: 5
## Sprint: 4" \
    "infrastructure,task" \
    "P1-high"

echo -e "${GREEN}=== Issue Generation Complete ===${NC}"
echo "Created 62 Phase 1 issues across all repositories"
echo ""
echo "Next steps:"
echo "1. Review issues in GitHub"
echo "2. Run: ./scripts/auto-implement-all.sh"
echo "3. Monitor progress in GitHub Projects"
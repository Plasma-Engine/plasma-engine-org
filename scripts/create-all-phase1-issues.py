#!/usr/bin/env python3
"""
Complete Phase 1 Issue Creation Script for Plasma Engine
Creates all 63 GitHub issues with proper formatting and dependencies
"""

import json
import subprocess
import sys
from typing import Dict, List

# Repository configuration
REPO = "Plasma-Engine/plasma-engine-org"

# Issue definitions
ISSUES = {
    # CodeRabbit Setup
    "PE-000": {
        "title": "[Infrastructure-Task] Configure CodeRabbit for automated PR reviews",
        "labels": ["infrastructure", "task", "phase-1", "P0-critical", "cursor-ready"],
        "milestone": "Sprint 1: Foundation (Weeks 1-2)",
        "points": 2,
        "body": """## Summary
Set up CodeRabbit for automated pull request reviews to ensure code quality and consistency.

## Acceptance Criteria
- [ ] CodeRabbit configuration file created
- [ ] GitHub App installed and configured
- [ ] Review rules customized for project standards
- [ ] Integration tested with sample PR
- [ ] Documentation updated

## Definition of Done
- [ ] Configuration committed
- [ ] GitHub App installed
- [ ] Test PR reviewed by CodeRabbit
- [ ] Team trained on feedback
- [ ] Documentation complete"""
    },

    # Infrastructure Issues
    "PE-601": {
        "title": "[Infra-Task] Set up local development environment",
        "labels": ["infrastructure", "task", "phase-1", "P0-critical", "cursor-ready"],
        "milestone": "Sprint 1: Foundation (Weeks 1-2)",
        "points": 5,
        "dependencies": {"blocks": ["all"]},
        "body": """## Summary
Create comprehensive local development environment using Docker Compose.

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
- Makefile with common commands
- .env.example files

## Definition of Done
- [ ] All services start successfully
- [ ] Hot reload verified
- [ ] Documentation complete
- [ ] CodeRabbit review passed"""
    },

    "PE-602": {
        "title": "[Infra-Task] Configure shared databases",
        "labels": ["infrastructure", "task", "phase-1", "P0-critical", "cursor-ready"],
        "milestone": "Sprint 1: Foundation (Weeks 1-2)",
        "points": 5,
        "dependencies": {"blocks": ["all-services"]},
        "body": """## Summary
Set up PostgreSQL with pgvector, Redis, Neo4j, and TimescaleDB.

## Acceptance Criteria
- [ ] PostgreSQL with pgvector extension
- [ ] Redis with persistence
- [ ] Neo4j configured
- [ ] TimescaleDB extension
- [ ] Backup strategies

## Technical Details
- PostgreSQL 15 with pgvector
- Redis 7.x with AOF persistence
- Neo4j 5.x Community
- TimescaleDB 2.x
- Automated backups with pg_dump

## Definition of Done
- [ ] All databases running
- [ ] Connection strings documented
- [ ] Backup scripts tested
- [ ] CodeRabbit review passed"""
    },

    "PE-603": {
        "title": "[Shared-Task] Create shared Python package",
        "labels": ["shared", "task", "phase-1", "P1-high", "cursor-ready"],
        "milestone": "Sprint 1: Foundation (Weeks 1-2)",
        "points": 3,
        "dependencies": {"requires": ["PE-602"]},
        "body": """## Summary
Create shared Python package with common utilities for all services.

## Acceptance Criteria
- [ ] Common utilities module
- [ ] Shared database models
- [ ] Authentication helpers
- [ ] Error handling utilities
- [ ] Package published to private registry

## Definition of Done
- [ ] Package structure created
- [ ] Tests passing
- [ ] Documentation complete
- [ ] CodeRabbit review passed"""
    },

    "PE-604": {
        "title": "[Infra-Feature] Implement centralized logging",
        "labels": ["infrastructure", "feature", "phase-1", "P1-high", "cursor-ready"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 5,
        "body": """## Summary
Set up centralized logging with ELK stack or similar.

## Acceptance Criteria
- [ ] Log aggregation configured
- [ ] Structured logging format
- [ ] Service correlation IDs
- [ ] Log retention policies
- [ ] Search and visualization

## Definition of Done
- [ ] All services logging to central system
- [ ] Dashboards created
- [ ] Alerts configured
- [ ] CodeRabbit review passed"""
    },

    "PE-605": {
        "title": "[Infra-Feature] Set up monitoring and metrics",
        "labels": ["infrastructure", "feature", "phase-1", "P1-high", "cursor-ready"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 8,
        "body": """## Summary
Implement monitoring with Prometheus and Grafana.

## Acceptance Criteria
- [ ] Prometheus metrics collection
- [ ] Grafana dashboards
- [ ] Service health monitoring
- [ ] Alert rules configured
- [ ] Performance baselines

## Definition of Done
- [ ] Metrics exported from all services
- [ ] Dashboards functional
- [ ] Alerts tested
- [ ] CodeRabbit review passed"""
    },

    "PE-606": {
        "title": "[Infra-Task] Configure CI/CD pipelines",
        "labels": ["infrastructure", "task", "phase-1", "P0-critical", "cursor-ready"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 8,
        "body": """## Summary
Set up GitHub Actions CI/CD pipelines for all services.

## Acceptance Criteria
- [ ] Build pipelines for all services
- [ ] Test automation
- [ ] Docker image building
- [ ] Security scanning
- [ ] Deployment workflows

## Definition of Done
- [ ] All pipelines green
- [ ] Tests running automatically
- [ ] Images pushed to registry
- [ ] CodeRabbit review passed"""
    },

    "PE-607": {
        "title": "[Infra-Task] Deploy to staging environment",
        "labels": ["infrastructure", "task", "phase-1", "P0-critical", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 8,
        "body": """## Summary
Deploy complete system to staging environment.

## Acceptance Criteria
- [ ] Kubernetes manifests created
- [ ] Services deployed
- [ ] Ingress configured
- [ ] SSL certificates
- [ ] Health checks passing

## Definition of Done
- [ ] All services accessible
- [ ] Integration tests passing
- [ ] Performance acceptable
- [ ] CodeRabbit review passed"""
    },

    "PE-608": {
        "title": "[Infra-Feature] Implement distributed tracing",
        "labels": ["infrastructure", "feature", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Add OpenTelemetry distributed tracing across services.

## Acceptance Criteria
- [ ] OpenTelemetry integration
- [ ] Trace collection configured
- [ ] Cross-service correlation
- [ ] Visualization setup
- [ ] Performance impact minimal

## Definition of Done
- [ ] Tracing working end-to-end
- [ ] Dashboards created
- [ ] Documentation complete
- [ ] CodeRabbit review passed"""
    },

    "PE-609": {
        "title": "[Infra-Task] Create backup and recovery procedures",
        "labels": ["infrastructure", "task", "phase-1", "P1-high", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Implement comprehensive backup and disaster recovery procedures.

## Acceptance Criteria
- [ ] Database backup automation
- [ ] File storage backup
- [ ] Recovery procedures documented
- [ ] Recovery time objectives met
- [ ] Regular backup testing

## Definition of Done
- [ ] Backups running automatically
- [ ] Recovery tested successfully
- [ ] Runbooks created
- [ ] CodeRabbit review passed"""
    },

    "PE-610": {
        "title": "[Infra-Feature] Implement secrets management",
        "labels": ["infrastructure", "feature", "phase-1", "P0-critical", "cursor-ready"],
        "milestone": "Sprint 1: Foundation (Weeks 1-2)",
        "points": 5,
        "body": """## Summary
Set up secure secrets management system.

## Acceptance Criteria
- [ ] Secrets vault configured
- [ ] Service authentication
- [ ] Rotation policies
- [ ] Audit logging
- [ ] Emergency procedures

## Definition of Done
- [ ] All secrets in vault
- [ ] Services authenticating
- [ ] Rotation working
- [ ] CodeRabbit review passed"""
    },

    "PE-611": {
        "title": "[Infra-Task] Performance testing and optimization",
        "labels": ["infrastructure", "task", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 8,
        "body": """## Summary
Conduct performance testing and implement optimizations.

## Acceptance Criteria
- [ ] Load testing completed
- [ ] Bottlenecks identified
- [ ] Optimizations implemented
- [ ] Performance targets met
- [ ] Monitoring in place

## Definition of Done
- [ ] Tests documented
- [ ] Performance acceptable
- [ ] Metrics dashboards updated
- [ ] CodeRabbit review passed"""
    },

    "PE-612": {
        "title": "[Infra-Task] Documentation and runbooks",
        "labels": ["infrastructure", "task", "phase-1", "P1-high", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Create comprehensive infrastructure documentation and runbooks.

## Acceptance Criteria
- [ ] Architecture documented
- [ ] Deployment procedures
- [ ] Troubleshooting guides
- [ ] Incident response plans
- [ ] Maintenance procedures

## Definition of Done
- [ ] All documentation complete
- [ ] Reviewed by team
- [ ] Accessible to all
- [ ] CodeRabbit review passed"""
    },

    # Gateway Issues
    "PE-101": {
        "title": "[Gateway-Feature] Implement JWT authentication middleware",
        "labels": ["gateway", "feature", "phase-1", "P0-critical", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 1: Foundation (Weeks 1-2)",
        "points": 5,
        "dependencies": {"requires": ["PE-601", "PE-602"]},
        "body": """## Summary
Create JWT-based authentication middleware for the GraphQL Gateway.

## Acceptance Criteria
- [ ] JWT validation middleware
- [ ] Role-based authorization
- [ ] Token refresh mechanism
- [ ] Rate limiting per user
- [ ] Security headers

## Technical Details
- Use jsonwebtoken library
- RS256 algorithm
- Redis for refresh tokens
- express-rate-limit integration

## Definition of Done
- [ ] Unit tests >90% coverage
- [ ] Integration tests passing
- [ ] Security audit complete
- [ ] CodeRabbit review passed"""
    },

    "PE-102": {
        "title": "[Gateway-Task] Set up TypeScript project structure",
        "labels": ["gateway", "task", "phase-1", "P0-critical", "cursor-ready"],
        "milestone": "Sprint 1: Foundation (Weeks 1-2)",
        "points": 2,
        "dependencies": {"requires": ["PE-601"]},
        "body": """## Summary
Initialize Gateway service with TypeScript and Express.

## Acceptance Criteria
- [ ] TypeScript configuration
- [ ] Express server setup
- [ ] Project structure organized
- [ ] Linting and formatting
- [ ] Docker configuration

## Definition of Done
- [ ] Service starts successfully
- [ ] TypeScript compiling
- [ ] Linting passing
- [ ] CodeRabbit review passed"""
    },

    "PE-103": {
        "title": "[Gateway-Feature] Set up GraphQL federation gateway",
        "labels": ["gateway", "feature", "phase-1", "P0-critical", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 8,
        "dependencies": {"requires": ["PE-101"], "blocks": ["all-graphql"]},
        "body": """## Summary
Configure Apollo Gateway for GraphQL federation.

## Acceptance Criteria
- [ ] Apollo Gateway configured
- [ ] Service discovery
- [ ] Schema composition
- [ ] Query planning optimized
- [ ] Introspection configured

## Technical Details
- Apollo Gateway 2.x
- Subgraph health checks
- Managed federation ready
- Query complexity analysis

## Definition of Done
- [ ] Federation working
- [ ] Performance benchmarks met
- [ ] Monitoring configured
- [ ] CodeRabbit review passed"""
    },

    "PE-104": {
        "title": "[Gateway-Feature] Implement request validation and sanitization",
        "labels": ["gateway", "feature", "phase-1", "P1-high", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 3,
        "body": """## Summary
Add comprehensive request validation and input sanitization.

## Acceptance Criteria
- [ ] Input validation middleware
- [ ] XSS prevention
- [ ] SQL injection prevention
- [ ] Request size limits
- [ ] Content-type validation

## Definition of Done
- [ ] Security tests passing
- [ ] Validation documented
- [ ] Performance acceptable
- [ ] CodeRabbit review passed"""
    },

    "PE-105": {
        "title": "[Gateway-Feature] Add response caching layer",
        "labels": ["gateway", "feature", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 5,
        "body": """## Summary
Implement intelligent response caching with Redis.

## Acceptance Criteria
- [ ] Redis cache integration
- [ ] Cache key strategies
- [ ] TTL configuration
- [ ] Cache invalidation
- [ ] Cache metrics

## Definition of Done
- [ ] Caching working
- [ ] Hit rates acceptable
- [ ] Invalidation tested
- [ ] CodeRabbit review passed"""
    },

    "PE-106": {
        "title": "[Gateway-Feature] Implement rate limiting and throttling",
        "labels": ["gateway", "feature", "phase-1", "P1-high", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 3,
        "body": """## Summary
Add rate limiting and request throttling.

## Acceptance Criteria
- [ ] Per-user rate limiting
- [ ] Per-IP rate limiting
- [ ] API key quotas
- [ ] Burst handling
- [ ] Rate limit headers

## Definition of Done
- [ ] Rate limiting working
- [ ] Tests comprehensive
- [ ] Documentation complete
- [ ] CodeRabbit review passed"""
    },

    "PE-107": {
        "title": "[Gateway-Feature] Add WebSocket support for subscriptions",
        "labels": ["gateway", "feature", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 5,
        "body": """## Summary
Implement WebSocket support for GraphQL subscriptions.

## Acceptance Criteria
- [ ] WebSocket server setup
- [ ] Subscription handling
- [ ] Connection management
- [ ] Authentication for WS
- [ ] Reconnection logic

## Definition of Done
- [ ] Subscriptions working
- [ ] Connection stable
- [ ] Tests passing
- [ ] CodeRabbit review passed"""
    },

    "PE-108": {
        "title": "[Gateway-Feature] Implement error handling and logging",
        "labels": ["gateway", "feature", "phase-1", "P1-high", "cursor-ready"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 3,
        "body": """## Summary
Add comprehensive error handling and structured logging.

## Acceptance Criteria
- [ ] Global error handler
- [ ] Error categorization
- [ ] Structured logging
- [ ] Correlation IDs
- [ ] Error metrics

## Definition of Done
- [ ] Errors handled gracefully
- [ ] Logging comprehensive
- [ ] Metrics exported
- [ ] CodeRabbit review passed"""
    },

    "PE-109": {
        "title": "[Gateway-Task] Create health check endpoints",
        "labels": ["gateway", "task", "phase-1", "P1-high", "cursor-ready"],
        "milestone": "Sprint 1: Foundation (Weeks 1-2)",
        "points": 2,
        "body": """## Summary
Implement health check and readiness endpoints.

## Acceptance Criteria
- [ ] /health endpoint
- [ ] /ready endpoint
- [ ] Dependency checks
- [ ] Response standards
- [ ] Kubernetes compatible

## Definition of Done
- [ ] Health checks working
- [ ] Dependencies verified
- [ ] K8s integration tested
- [ ] CodeRabbit review passed"""
    },

    "PE-110": {
        "title": "[Gateway-Task] Integration testing suite",
        "labels": ["gateway", "task", "phase-1", "P1-high", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Create comprehensive integration test suite.

## Acceptance Criteria
- [ ] End-to-end tests
- [ ] Federation tests
- [ ] Auth flow tests
- [ ] Error scenario tests
- [ ] Performance tests

## Definition of Done
- [ ] >80% coverage
- [ ] All tests passing
- [ ] CI integration
- [ ] CodeRabbit review passed"""
    },

    # Research Service Issues
    "PE-201": {
        "title": "[Research-Task] Set up Python service with async support",
        "labels": ["research", "task", "phase-1", "P0-critical", "cursor-ready"],
        "milestone": "Sprint 1: Foundation (Weeks 1-2)",
        "points": 3,
        "dependencies": {"requires": ["PE-602"]},
        "body": """## Summary
Initialize Research service with FastAPI and async support.

## Acceptance Criteria
- [ ] FastAPI application structure
- [ ] Async/await patterns
- [ ] Celery worker setup
- [ ] Redis queue configuration
- [ ] Docker containerization

## Technical Details
- Python 3.11+ with asyncio
- Celery 5.3+ with Redis
- SQLAlchemy 2.0 async
- Structured logging with structlog

## Definition of Done
- [ ] Service running
- [ ] Async patterns working
- [ ] Workers processing
- [ ] CodeRabbit review passed"""
    },

    "PE-202": {
        "title": "[Research-Feature] Implement document ingestion pipeline",
        "labels": ["research", "feature", "phase-1", "P0-critical", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 8,
        "dependencies": {"requires": ["PE-201"], "blocks": ["PE-203"]},
        "body": """## Summary
Build document ingestion pipeline for multiple formats.

## Acceptance Criteria
- [ ] Multi-format support (PDF, DOCX, MD, HTML)
- [ ] Chunking strategies
- [ ] Metadata extraction
- [ ] S3/MinIO storage
- [ ] Async processing

## Technical Details
- Unstructured.io for parsing
- Sliding window chunking
- Apache Tika for metadata
- Batch processing
- Deduplication logic

## Definition of Done
- [ ] All formats working
- [ ] Chunking optimized
- [ ] Storage reliable
- [ ] CodeRabbit review passed"""
    },

    "PE-203": {
        "title": "[Research-Feature] Create vector embedding system",
        "labels": ["research", "feature", "phase-1", "P0-critical", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 5,
        "dependencies": {"requires": ["PE-202"], "blocks": ["PE-204"]},
        "body": """## Summary
Implement vector embedding generation and storage.

## Acceptance Criteria
- [ ] OpenAI embeddings integration
- [ ] Local embedding option
- [ ] pgvector database setup
- [ ] Batch processing
- [ ] Embedding cache

## Technical Details
- text-embedding-3-large
- all-MiniLM-L6-v2 local
- HNSW index
- Batch optimization
- Redis caching

## Definition of Done
- [ ] Embeddings generating
- [ ] Storage optimized
- [ ] Cache working
- [ ] CodeRabbit review passed"""
    },

    "PE-204": {
        "title": "[Research-Feature] Build GraphRAG knowledge graph",
        "labels": ["research", "feature", "phase-1", "P0-critical", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 13,
        "dependencies": {"requires": ["PE-203"]},
        "body": """## Summary
Create GraphRAG knowledge graph system with Neo4j.

## Acceptance Criteria
- [ ] Neo4j integration
- [ ] Entity extraction
- [ ] Relationship mapping
- [ ] Graph traversal
- [ ] Knowledge synthesis

## Technical Details
- Neo4j 5.x with APOC
- spaCy for NER
- Custom relationships
- Cypher optimization
- Node2Vec embeddings

## Definition of Done
- [ ] Graph populated
- [ ] Queries optimized
- [ ] Synthesis working
- [ ] CodeRabbit review passed"""
    },

    "PE-205": {
        "title": "[Research-Feature] Implement semantic search API",
        "labels": ["research", "feature", "phase-1", "P0-critical", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 5,
        "dependencies": {"requires": ["PE-203", "PE-204"]},
        "body": """## Summary
Build semantic search API with hybrid search capabilities.

## Acceptance Criteria
- [ ] Vector similarity search
- [ ] Hybrid search
- [ ] Query expansion
- [ ] Result ranking
- [ ] GraphQL resolver

## Technical Details
- Cosine similarity
- BM25 keyword matching
- Query understanding
- MMR for diversity
- Pagination support

## Definition of Done
- [ ] Search accurate
- [ ] Performance good
- [ ] API documented
- [ ] CodeRabbit review passed"""
    },

    "PE-206": {
        "title": "[Research-Task] Create RAG query engine",
        "labels": ["research", "task", "phase-1", "P1-high", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 8,
        "dependencies": {"requires": ["PE-205"]},
        "body": """## Summary
Implement RAG query engine with LangChain.

## Acceptance Criteria
- [ ] Context retrieval
- [ ] Prompt engineering
- [ ] LangChain integration
- [ ] Streaming responses
- [ ] Source attribution

## Technical Details
- LangChain 0.1+ LCEL
- Context management
- Chain-of-thought
- Hallucination detection
- Citation formatting

## Definition of Done
- [ ] RAG working
- [ ] Accuracy high
- [ ] Citations correct
- [ ] CodeRabbit review passed"""
    },

    "PE-207": {
        "title": "[Research-Feature] Implement incremental learning system",
        "labels": ["research", "feature", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 5,
        "dependencies": {"requires": ["PE-204"]},
        "body": """## Summary
Build incremental learning for knowledge updates.

## Acceptance Criteria
- [ ] Incremental updates
- [ ] Concept drift detection
- [ ] Version control
- [ ] Conflict resolution
- [ ] Rollback capability

## Definition of Done
- [ ] Updates working
- [ ] Versioning functional
- [ ] Conflicts handled
- [ ] CodeRabbit review passed"""
    },

    "PE-208": {
        "title": "[Research-Feature] Build knowledge validation system",
        "labels": ["research", "feature", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "dependencies": {"requires": ["PE-206"]},
        "body": """## Summary
Create knowledge validation and fact-checking system.

## Acceptance Criteria
- [ ] Fact checking
- [ ] Consistency validation
- [ ] Quality scoring
- [ ] Review workflow
- [ ] Auto corrections

## Definition of Done
- [ ] Validation working
- [ ] Quality metrics defined
- [ ] Workflow functional
- [ ] CodeRabbit review passed"""
    },

    "PE-209": {
        "title": "[Research-Task] Create knowledge export/import tools",
        "labels": ["research", "task", "phase-1", "P3-low", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 3,
        "dependencies": {"requires": ["PE-204"]},
        "body": """## Summary
Build tools for knowledge base import/export.

## Acceptance Criteria
- [ ] Export formats (JSON-LD, RDF, GraphML)
- [ ] Bulk import
- [ ] Schema mapping
- [ ] Transformations
- [ ] Progress tracking

## Definition of Done
- [ ] Import/export working
- [ ] Formats validated
- [ ] Performance acceptable
- [ ] CodeRabbit review passed"""
    },

    "PE-210": {
        "title": "[Research-Feature] Implement multi-modal search",
        "labels": ["research", "feature", "phase-1", "P3-low", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 8,
        "dependencies": {"requires": ["PE-205"]},
        "body": """## Summary
Add multi-modal search capabilities.

## Acceptance Criteria
- [ ] Image search
- [ ] Table understanding
- [ ] Code search
- [ ] Audio transcription
- [ ] Cross-modal retrieval

## Technical Details
- CLIP for images
- Camelot for tables
- CodeBERT for code
- Whisper for audio

## Definition of Done
- [ ] All modes working
- [ ] Unified interface
- [ ] Performance good
- [ ] CodeRabbit review passed"""
    },

    # Brand Service Issues (with Apify modifications)
    "PE-301": {
        "title": "[Brand-Task] Set up service with Celery and scheduled tasks",
        "labels": ["brand", "task", "phase-1", "P0-critical", "cursor-ready"],
        "milestone": "Sprint 1: Foundation (Weeks 1-2)",
        "points": 3,
        "dependencies": {"requires": ["PE-602"]},
        "body": """## Summary
Initialize Brand service with FastAPI and Celery for social media monitoring.

## Acceptance Criteria
- [ ] FastAPI structure
- [ ] Celery beat scheduler
- [ ] Redis queue
- [ ] Database models
- [ ] Docker configuration

## Definition of Done
- [ ] Service running
- [ ] Scheduler working
- [ ] Tasks processing
- [ ] CodeRabbit review passed"""
    },

    "PE-302": {
        "title": "[Brand-Feature] Implement X/Twitter collector using Apify",
        "labels": ["brand", "feature", "phase-1", "P0-critical", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 8,
        "dependencies": {"requires": ["PE-301"], "blocks": ["PE-304"]},
        "body": """## Summary
Build X/Twitter data collection using Apify Twitter Scraper.

## Acceptance Criteria
- [ ] Apify client integrated
- [ ] Twitter Scraper configured
- [ ] Mention tracking
- [ ] Hashtag monitoring
- [ ] Timeline collection
- [ ] Data normalization

## Technical Details
- Apify Twitter Scraper Actor
- Proxy rotation
- Webhook notifications
- Rate limit handling
- Data caching in Redis

## Implementation Notes
- No direct Twitter API needed
- Use Apify credits efficiently
- Implement incremental collection

## Definition of Done
- [ ] Collection reliable
- [ ] Data normalized
- [ ] Monitoring dashboard
- [ ] CodeRabbit review passed"""
    },

    "PE-303": {
        "title": "[Brand-Feature] Build Reddit monitoring using Apify",
        "labels": ["brand", "feature", "phase-1", "P1-high", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 5,
        "dependencies": {"requires": ["PE-301"], "blocks": ["PE-304"]},
        "body": """## Summary
Implement Reddit monitoring with Apify Reddit Scraper.

## Acceptance Criteria
- [ ] Apify Reddit Scraper integrated
- [ ] Subreddit monitoring
- [ ] Comment tracking
- [ ] Keyword alerts
- [ ] Sentiment preprocessing

## Technical Details
- Apify Reddit Scraper Actor
- Incremental data collection
- Comment tree structure
- Keyword matching
- Alert notifications

## Implementation Notes
- No Reddit API required
- Handle deleted content
- Store comment relationships

## Definition of Done
- [ ] Monitoring working
- [ ] Alerts functional
- [ ] Data pipeline stable
- [ ] CodeRabbit review passed"""
    },

    "PE-304": {
        "title": "[Brand-Feature] Create sentiment analysis pipeline",
        "labels": ["brand", "feature", "phase-1", "P0-critical", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 8,
        "dependencies": {"requires": ["PE-302", "PE-303"]},
        "body": """## Summary
Build sentiment analysis pipeline for social media data.

## Acceptance Criteria
- [ ] Transformer models
- [ ] Multi-language support
- [ ] Aspect-based sentiment
- [ ] Emotion detection
- [ ] Batch processing

## Technical Details
- RoBERTa for sentiment
- XLM-RoBERTa multilingual
- spaCy for aspects
- GPU acceleration

## Definition of Done
- [ ] Analysis accurate
- [ ] Performance optimized
- [ ] Languages supported
- [ ] CodeRabbit review passed"""
    },

    "PE-305": {
        "title": "[Brand-Feature] Implement trend detection system",
        "labels": ["brand", "feature", "phase-1", "P1-high", "cursor-ready"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 5,
        "dependencies": {"requires": ["PE-304"]},
        "body": """## Summary
Create trend detection and analysis system.

## Acceptance Criteria
- [ ] Trend identification
- [ ] Anomaly detection
- [ ] Topic modeling
- [ ] Velocity tracking
- [ ] Alert system

## Definition of Done
- [ ] Trends detected accurately
- [ ] Alerts working
- [ ] Dashboard created
- [ ] CodeRabbit review passed"""
    },

    "PE-306": {
        "title": "[Brand-Feature] Build influencer identification system",
        "labels": ["brand", "feature", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 5,
        "body": """## Summary
Identify and track key influencers in brand mentions.

## Acceptance Criteria
- [ ] Influencer scoring
- [ ] Network analysis
- [ ] Engagement metrics
- [ ] Reach calculation
- [ ] Profile building

## Definition of Done
- [ ] Influencers identified
- [ ] Metrics accurate
- [ ] Profiles complete
- [ ] CodeRabbit review passed"""
    },

    "PE-307": {
        "title": "[Brand-Feature] Create competitor analysis module",
        "labels": ["brand", "feature", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 8,
        "body": """## Summary
Build competitor tracking and analysis system.

## Acceptance Criteria
- [ ] Competitor identification
- [ ] Mention comparison
- [ ] Share of voice
- [ ] Sentiment comparison
- [ ] Reporting dashboard

## Definition of Done
- [ ] Tracking working
- [ ] Comparisons accurate
- [ ] Dashboard functional
- [ ] CodeRabbit review passed"""
    },

    "PE-308": {
        "title": "[Brand-Feature] Implement crisis detection system",
        "labels": ["brand", "feature", "phase-1", "P1-high", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Create early warning system for brand crises.

## Acceptance Criteria
- [ ] Negative spike detection
- [ ] Velocity tracking
- [ ] Alert escalation
- [ ] Response workflows
- [ ] Historical analysis

## Definition of Done
- [ ] Detection accurate
- [ ] Alerts timely
- [ ] Workflows defined
- [ ] CodeRabbit review passed"""
    },

    "PE-309": {
        "title": "[Brand-Task] Create brand health dashboard",
        "labels": ["brand", "task", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Build comprehensive brand health monitoring dashboard.

## Acceptance Criteria
- [ ] Real-time metrics
- [ ] Historical trends
- [ ] Sentiment gauges
- [ ] Alert indicators
- [ ] Export capabilities

## Definition of Done
- [ ] Dashboard complete
- [ ] Data real-time
- [ ] Exports working
- [ ] CodeRabbit review passed"""
    },

    "PE-310": {
        "title": "[Brand-Feature] Build reporting and insights engine",
        "labels": ["brand", "feature", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Create automated reporting and insights generation.

## Acceptance Criteria
- [ ] Automated reports
- [ ] Insight generation
- [ ] Trend summaries
- [ ] Recommendations
- [ ] Distribution system

## Definition of Done
- [ ] Reports generating
- [ ] Insights valuable
- [ ] Distribution working
- [ ] CodeRabbit review passed"""
    },

    # Content Service Issues
    "PE-401": {
        "title": "[Content-Task] Set up FastAPI with LangChain integration",
        "labels": ["content", "task", "phase-1", "P0-critical", "cursor-ready"],
        "milestone": "Sprint 1: Foundation (Weeks 1-2)",
        "points": 3,
        "dependencies": {"requires": ["PE-602"]},
        "body": """## Summary
Initialize Content service with LangChain for content generation.

## Acceptance Criteria
- [ ] FastAPI structure
- [ ] LangChain integrated
- [ ] LLM clients configured
- [ ] Content models
- [ ] Docker setup

## Definition of Done
- [ ] Service running
- [ ] LangChain working
- [ ] Tests passing
- [ ] CodeRabbit review passed"""
    },

    "PE-402": {
        "title": "[Content-Feature] Implement blog post generation",
        "labels": ["content", "feature", "phase-1", "P0-critical", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 8,
        "body": """## Summary
Build blog post generation with multiple styles and formats.

## Acceptance Criteria
- [ ] Style templates
- [ ] Topic research
- [ ] Outline generation
- [ ] Content creation
- [ ] SEO optimization

## Definition of Done
- [ ] Generation working
- [ ] Quality high
- [ ] SEO optimized
- [ ] CodeRabbit review passed"""
    },

    "PE-403": {
        "title": "[Content-Feature] Create social media content generator",
        "labels": ["content", "feature", "phase-1", "P1-high", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 5,
        "body": """## Summary
Generate platform-specific social media content.

## Acceptance Criteria
- [ ] Platform templates
- [ ] Character limits
- [ ] Hashtag generation
- [ ] Image suggestions
- [ ] Thread creation

## Definition of Done
- [ ] All platforms supported
- [ ] Content engaging
- [ ] Limits respected
- [ ] CodeRabbit review passed"""
    },

    "PE-404": {
        "title": "[Content-Feature] Build email campaign generator",
        "labels": ["content", "feature", "phase-1", "P1-high", "cursor-ready"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 5,
        "body": """## Summary
Create email campaign content generation system.

## Acceptance Criteria
- [ ] Campaign templates
- [ ] Personalization
- [ ] A/B variations
- [ ] Subject optimization
- [ ] CTA generation

## Definition of Done
- [ ] Emails generating
- [ ] Personalization working
- [ ] Templates diverse
- [ ] CodeRabbit review passed"""
    },

    "PE-405": {
        "title": "[Content-Feature] Implement content optimization engine",
        "labels": ["content", "feature", "phase-1", "P1-high", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 8,
        "body": """## Summary
Build content optimization for SEO and engagement.

## Acceptance Criteria
- [ ] SEO analysis
- [ ] Readability scoring
- [ ] Keyword optimization
- [ ] Meta generation
- [ ] Structure improvement

## Definition of Done
- [ ] Optimization effective
- [ ] Scores improved
- [ ] SEO enhanced
- [ ] CodeRabbit review passed"""
    },

    "PE-406": {
        "title": "[Content-Feature] Create multi-platform publishing system",
        "labels": ["content", "feature", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 8,
        "body": """## Summary
Build system to publish content across multiple platforms.

## Acceptance Criteria
- [ ] Platform integrations
- [ ] Format conversion
- [ ] Schedule management
- [ ] Cross-posting
- [ ] Analytics tracking

## Definition of Done
- [ ] Publishing working
- [ ] Platforms integrated
- [ ] Scheduling functional
- [ ] CodeRabbit review passed"""
    },

    "PE-407": {
        "title": "[Content-Feature] Build content personalization system",
        "labels": ["content", "feature", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Create dynamic content personalization based on user data.

## Acceptance Criteria
- [ ] User profiling
- [ ] Content adaptation
- [ ] A/B testing
- [ ] Performance tracking
- [ ] Recommendation engine

## Definition of Done
- [ ] Personalization working
- [ ] Metrics improved
- [ ] Testing functional
- [ ] CodeRabbit review passed"""
    },

    "PE-408": {
        "title": "[Content-Task] Implement content versioning system",
        "labels": ["content", "task", "phase-1", "P3-low", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 3,
        "body": """## Summary
Build version control for generated content.

## Acceptance Criteria
- [ ] Version tracking
- [ ] Diff generation
- [ ] Rollback capability
- [ ] Approval workflows
- [ ] Audit trail

## Definition of Done
- [ ] Versioning working
- [ ] History tracked
- [ ] Rollback tested
- [ ] CodeRabbit review passed"""
    },

    "PE-409": {
        "title": "[Content-Feature] Create content repurposing engine",
        "labels": ["content", "feature", "phase-1", "P3-low", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Build system to repurpose content across formats.

## Acceptance Criteria
- [ ] Format conversion
- [ ] Length adaptation
- [ ] Style transformation
- [ ] Media extraction
- [ ] Quality preservation

## Definition of Done
- [ ] Repurposing working
- [ ] Quality maintained
- [ ] Formats supported
- [ ] CodeRabbit review passed"""
    },

    "PE-410": {
        "title": "[Content-Feature] Build content performance analytics",
        "labels": ["content", "feature", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Create analytics system for content performance tracking.

## Acceptance Criteria
- [ ] Engagement metrics
- [ ] Conversion tracking
- [ ] A/B test results
- [ ] ROI calculation
- [ ] Reporting dashboard

## Definition of Done
- [ ] Analytics accurate
- [ ] Dashboard functional
- [ ] Reports generating
- [ ] CodeRabbit review passed"""
    },

    # Agent Service Issues
    "PE-501": {
        "title": "[Agent-Task] Initialize service with MCP protocol support",
        "labels": ["agent", "task", "phase-1", "P0-critical", "cursor-ready"],
        "milestone": "Sprint 1: Foundation (Weeks 1-2)",
        "points": 5,
        "dependencies": {"requires": ["PE-602"]},
        "body": """## Summary
Set up Agent service with Model Context Protocol support.

## Acceptance Criteria
- [ ] FastAPI structure
- [ ] MCP server configured
- [ ] Tool registry
- [ ] WebSocket support
- [ ] Docker setup

## Technical Details
- MCP protocol spec
- Tool discovery
- Version management
- WebSocket handling

## Definition of Done
- [ ] Service running
- [ ] MCP functional
- [ ] Tools callable
- [ ] CodeRabbit review passed"""
    },

    "PE-502": {
        "title": "[Agent-Feature] Implement core MCP tools",
        "labels": ["agent", "feature", "phase-1", "P0-critical", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 2: Core Services (Weeks 3-4)",
        "points": 8,
        "dependencies": {"requires": ["PE-501"]},
        "body": """## Summary
Build essential MCP tools for agent operations.

## Acceptance Criteria
- [ ] Search tool
- [ ] Database tool
- [ ] API call tool
- [ ] File system tool
- [ ] Calculation tool

## Definition of Done
- [ ] Tools implemented
- [ ] Tests comprehensive
- [ ] Documentation complete
- [ ] CodeRabbit review passed"""
    },

    "PE-503": {
        "title": "[Agent-Feature] Create workflow orchestration engine",
        "labels": ["agent", "feature", "phase-1", "P0-critical", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 13,
        "dependencies": {"requires": ["PE-502"]},
        "body": """## Summary
Build workflow engine for complex agent tasks.

## Acceptance Criteria
- [ ] Workflow definition
- [ ] Step execution
- [ ] Conditional logic
- [ ] Error handling
- [ ] State management

## Definition of Done
- [ ] Workflows executing
- [ ] State persisted
- [ ] Errors handled
- [ ] CodeRabbit review passed"""
    },

    "PE-504": {
        "title": "[Agent-Feature] Implement multi-agent coordination",
        "labels": ["agent", "feature", "phase-1", "P1-high", "cursor-ready", "needs-coderabbit-review"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 8,
        "dependencies": {"requires": ["PE-503"]},
        "body": """## Summary
Build system for coordinating multiple agents.

## Acceptance Criteria
- [ ] Agent spawning
- [ ] Task distribution
- [ ] Communication protocol
- [ ] Result aggregation
- [ ] Conflict resolution

## Definition of Done
- [ ] Coordination working
- [ ] Communication reliable
- [ ] Results accurate
- [ ] CodeRabbit review passed"""
    },

    "PE-505": {
        "title": "[Agent-Feature] Build agent memory system",
        "labels": ["agent", "feature", "phase-1", "P1-high", "cursor-ready"],
        "milestone": "Sprint 3: AI Integration (Weeks 5-6)",
        "points": 5,
        "body": """## Summary
Create persistent memory system for agents.

## Acceptance Criteria
- [ ] Short-term memory
- [ ] Long-term storage
- [ ] Context retrieval
- [ ] Memory pruning
- [ ] Cross-session persistence

## Definition of Done
- [ ] Memory working
- [ ] Retrieval accurate
- [ ] Persistence reliable
- [ ] CodeRabbit review passed"""
    },

    "PE-506": {
        "title": "[Agent-Feature] Implement tool learning system",
        "labels": ["agent", "feature", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 8,
        "body": """## Summary
Build system for agents to learn new tool usage.

## Acceptance Criteria
- [ ] Tool discovery
- [ ] Usage learning
- [ ] Pattern recognition
- [ ] Success tracking
- [ ] Optimization

## Definition of Done
- [ ] Learning functional
- [ ] Patterns recognized
- [ ] Usage improved
- [ ] CodeRabbit review passed"""
    },

    "PE-507": {
        "title": "[Agent-Task] Create agent monitoring dashboard",
        "labels": ["agent", "task", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Build dashboard for monitoring agent activities.

## Acceptance Criteria
- [ ] Activity tracking
- [ ] Performance metrics
- [ ] Error monitoring
- [ ] Resource usage
- [ ] Real-time updates

## Definition of Done
- [ ] Dashboard functional
- [ ] Metrics accurate
- [ ] Updates real-time
- [ ] CodeRabbit review passed"""
    },

    "PE-508": {
        "title": "[Agent-Feature] Build agent reasoning tracer",
        "labels": ["agent", "feature", "phase-1", "P3-low", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Create system to trace and explain agent reasoning.

## Acceptance Criteria
- [ ] Decision tracking
- [ ] Reasoning chains
- [ ] Explanation generation
- [ ] Visualization
- [ ] Export capability

## Definition of Done
- [ ] Tracing working
- [ ] Explanations clear
- [ ] Visualization helpful
- [ ] CodeRabbit review passed"""
    },

    "PE-509": {
        "title": "[Agent-Feature] Implement agent templates",
        "labels": ["agent", "feature", "phase-1", "P3-low", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 3,
        "body": """## Summary
Create reusable agent templates for common tasks.

## Acceptance Criteria
- [ ] Template definition
- [ ] Parameter system
- [ ] Customization
- [ ] Template library
- [ ] Version control

## Definition of Done
- [ ] Templates working
- [ ] Library organized
- [ ] Customization easy
- [ ] CodeRabbit review passed"""
    },

    "PE-510": {
        "title": "[Agent-Task] Performance optimization and testing",
        "labels": ["agent", "task", "phase-1", "P2-medium", "cursor-ready"],
        "milestone": "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "points": 5,
        "body": """## Summary
Optimize agent performance and conduct load testing.

## Acceptance Criteria
- [ ] Performance profiling
- [ ] Bottleneck identification
- [ ] Optimization implementation
- [ ] Load testing
- [ ] Benchmarking

## Definition of Done
- [ ] Performance improved
- [ ] Load tests passing
- [ ] Benchmarks documented
- [ ] CodeRabbit review passed"""
    }
}


def create_label(label: str, color: str, description: str = ""):
    """Create a GitHub label"""
    cmd = [
        "gh", "label", "create", label,
        "--color", color,
        "--description", description,
        "--repo", REPO
    ]
    try:
        subprocess.run(cmd, check=False, capture_output=True)
    except:
        pass  # Label might already exist


def create_milestone(title: str, description: str, due_date: str):
    """Create a GitHub milestone"""
    cmd = [
        "gh", "api", f"repos/{REPO}/milestones",
        "--method", "POST",
        "-f", f"title={title}",
        "-f", f"description={description}",
        "-f", f"due_on={due_date}"
    ]
    try:
        subprocess.run(cmd, check=False, capture_output=True)
    except:
        pass  # Milestone might already exist


def create_issue(ticket_id: str, issue_data: Dict):
    """Create a GitHub issue"""
    title = f"{issue_data['title']} ({ticket_id})"
    body = issue_data['body']
    labels = ",".join(issue_data['labels'])
    milestone = issue_data['milestone']

    cmd = [
        "gh", "issue", "create",
        "--repo", REPO,
        "--title", title,
        "--body", body,
        "--label", labels,
        "--milestone", milestone
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created {ticket_id}: {issue_data['title']}")
        else:
            print(f"❌ Failed {ticket_id}: {result.stderr}")
    except Exception as e:
        print(f"❌ Error creating {ticket_id}: {e}")


def main():
    print("🚀 Phase 1 Issue Creation for Plasma Engine")
    print("=" * 50)

    # Create labels
    print("\n📌 Creating labels...")
    create_label("P0-critical", "FF0000", "System down, data loss, security vulnerability")
    create_label("P1-high", "FF6600", "Core functionality broken, blocking other work")
    create_label("P2-medium", "FFAA00", "Important but not blocking, workarounds exist")
    create_label("P3-low", "FFFF00", "Nice to have, minor improvements")

    create_label("gateway", "0E8A16", "Gateway service")
    create_label("research", "1D76DB", "Research service")
    create_label("brand", "5319E7", "Brand service")
    create_label("content", "B60205", "Content service")
    create_label("agent", "FBCA04", "Agent service")
    create_label("infrastructure", "006B75", "Infrastructure and DevOps")
    create_label("shared", "84B6EB", "Shared components")

    create_label("feature", "A2EEEF", "New functionality")
    create_label("task", "D4C5F9", "Task or chore")
    create_label("spike", "FFDAB9", "Research or investigation")
    create_label("adr", "98FB98", "Architecture Decision Record")

    create_label("phase-1", "2EA44F", "Phase 1 implementation")
    create_label("needs-coderabbit-review", "FFD700", "Requires CodeRabbit review")
    create_label("cursor-ready", "00CED1", "Ready for cursor agent implementation")

    # Create milestones
    print("\n📅 Creating milestones...")
    create_milestone(
        "Sprint 1: Foundation (Weeks 1-2)",
        "Environment setup, authentication, service scaffolding",
        "2025-10-13T23:59:59Z"
    )
    create_milestone(
        "Sprint 2: Core Services (Weeks 3-4)",
        "API implementation, data pipelines, GraphQL federation",
        "2025-10-27T23:59:59Z"
    )
    create_milestone(
        "Sprint 3: AI Integration (Weeks 5-6)",
        "Advanced features, AI capabilities, workflow engine",
        "2025-11-10T23:59:59Z"
    )
    create_milestone(
        "Sprint 4: Polish & Deploy (Weeks 7-8)",
        "Testing, monitoring, staging deployment",
        "2025-11-24T23:59:59Z"
    )

    # Create issues
    print("\n📝 Creating issues...")
    total = len(ISSUES)
    created = 0

    for ticket_id, issue_data in ISSUES.items():
        create_issue(ticket_id, issue_data)
        created += 1
        print(f"Progress: {created}/{total} ({created*100//total}%)")

    print("\n" + "=" * 50)
    print(f"✅ Complete! Created {created} issues.")
    print("\nNext steps:")
    print("1. Review issues at https://github.com/Plasma-Engine/plasma-engine-org/issues")
    print("2. Create project board for tracking")
    print("3. Assign issues to cursor agents")
    print("4. Begin Sprint 1 implementation")


if __name__ == "__main__":
    main()
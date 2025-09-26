# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

The **Plasma Engine** is an enterprise AI platform consisting of multiple microservices for research automation, brand intelligence, and content orchestration. This is a mono-repository containing seven service repositories and shared infrastructure.

## Architecture

The platform follows a microservices architecture with GraphQL federation:

```
Clients → Gateway (GraphQL Federation) → [Research|Brand|Content|Agent] Services
                     ↓
           Infrastructure Services (PostgreSQL, Redis, Neo4j)
```

### Service Responsibilities

- **Gateway** (`plasma-engine-gateway`): API gateway, authentication, GraphQL federation (TypeScript/Apollo)
- **Research** (`plasma-engine-research`): GraphRAG system, knowledge management, vector search (Python/FastAPI)  
- **Brand** (`plasma-engine-brand`): Brand monitoring, sentiment analysis, social media tracking (Python/FastAPI)
- **Content** (`plasma-engine-content`): AI content generation, publishing workflows (Python/FastAPI)
- **Agent** (`plasma-engine-agent`): Multi-agent orchestration, MCP support, browser automation (Python/FastAPI)
- **Shared** (`plasma-engine-shared`): Common templates, libraries, documentation
- **Infra** (`plasma-engine-infra`): CI/CD workflows, Terraform modules, Docker Compose

## Development Commands

### Environment Setup
```bash
# Clone all repositories
make clone-all

# Complete development environment setup
make setup

# Install dependencies for all services
make install-deps

# Initialize all databases
make init-db
```

### Service Management
```bash
# Start infrastructure services (PostgreSQL, Redis, etc.)
make start-infra

# Run individual services
make run-gateway      # Port 3000 (TypeScript/Node)
make run-research     # Port 8000 (Python/FastAPI)
make run-brand        # Port 8001 (Python/FastAPI) 
make run-content      # Port 8002 (Python/FastAPI)
make run-agent        # Port 8003 (Python/FastAPI)

# Run all services in tmux session
make run-all
```

### Testing & Quality
```bash
# Run tests for all services
make test-all

# Run linting for all services  
make lint-all

# Individual service commands (when inside service directory):
# Python services: pytest, uvicorn app.main:app --reload
# TypeScript services: pnpm test, pnpm dev
```

### Repository Management
```bash
# Pull latest changes for all repos
make pull-all

# Show git status for all repos
make status-all

# Sync shared templates across repositories
make sync-templates
```

### Docker Operations
```bash
# Build Docker images for all services
make build-all

# Push images to registry
make push-all

# View infrastructure logs
make logs

# Show running services
make ps
```

## Key Development Patterns

### Service Communication
- All external communication flows through the Gateway service
- Internal service communication uses direct HTTP/GraphQL calls
- Event-driven patterns use Redis for pub/sub messaging

### Database Strategy
- Each service has its own PostgreSQL database for data isolation
- Research service uses Neo4j for knowledge graph storage
- Shared Redis instance for caching and session management

### AI/ML Integration
- Research service: LangChain, LlamaIndex for RAG workflows
- Content service: OpenAI, Anthropic APIs for generation
- Brand service: Transformers, spaCy for NLP tasks
- Agent service: Multi-agent orchestration with MCP protocol

### Async Processing
- Python services use Celery + Redis for background tasks
- Long-running operations (document processing, content generation) are queued
- Agent service supports parallel execution and checkpoint/resume

## Testing Strategy

- **Python services**: pytest with fixtures for database/external APIs
- **TypeScript services**: Jest/Vitest with mocking
- **Integration tests**: Docker Compose for full stack testing
- **CI/CD**: GitHub Actions with security scanning and automated reviews

## Development Workflow

1. Use `make clone-all` to set up all repositories locally
2. Run `make setup` for complete environment initialization  
3. Use `make run-all` to start all services in development mode
4. Each service follows the shared development handbook in `plasma-engine-shared/docs/`
5. All PRs require CodeRabbit review + human approval
6. Services use reusable workflows from `plasma-engine-infra`

## Common Debugging

### Service Won't Start
- Check if infrastructure is running: `make ps`
- Verify database initialization: `make init-db`
- Check service-specific README for dependencies

### Database Issues
- Restart infrastructure: `make stop-infra && make start-infra`
- Check database logs: `make logs`
- Verify connection strings in `.env` files

### Performance Issues
- Monitor Redis for cache hit rates
- Check PostgreSQL query performance
- Review Celery task queue backlogs

## External Dependencies

- **Databases**: PostgreSQL, Redis, Neo4j (via Docker Compose)
- **AI Services**: OpenAI, Anthropic, Stability AI APIs
- **Search**: Elasticsearch, pgvector, Pinecone
- **Monitoring**: OpenTelemetry, Prometheus
- **Browser Automation**: Playwright (Agent service)

## Environment Variables

Each service requires its own `.env` file copied from `.env.example`. Key shared variables:
- Database connection strings
- AI service API keys  
- Redis configuration
- Authentication providers (Auth0/Clerk)
- External API credentials (social media, news sources)
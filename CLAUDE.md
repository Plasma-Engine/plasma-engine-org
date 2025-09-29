# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Plasma Engine is an enterprise AI platform with multiple microservices for research automation, brand intelligence, and content orchestration. This mono-repository manages seven service repositories using a microservices architecture with GraphQL federation.

The platform includes web scraping capabilities via BrightData and ScraperAPI integrations, supporting social media monitoring, content extraction, and automated data collection workflows.

## Essential Build & Test Commands

### Repository-Wide Commands (from root)
```bash
# Initial setup
make setup                   # Complete development environment setup (includes clone-all, install-deps, init-db)
make install-deps           # Install dependencies for all services

# Running services
make run-all                # Start all services in tmux session
make run-gateway           # Run Gateway service (port 3000)
make run-research          # Run Research service (port 8000)
make run-brand            # Run Brand service (port 8001)
make run-content          # Run Content service (port 8002)
make run-agent            # Run Agent service (port 8003)

# Testing
make test-all              # Run tests for all services
make lint-all              # Run linting for all services

# Infrastructure
make start-infra           # Start Docker infrastructure (PostgreSQL, Redis, Neo4j)
make stop-infra            # Stop infrastructure services
```

### Service-Specific Commands

#### Gateway Service (TypeScript/Node.js)
```bash
cd plasma-engine-gateway
npm ci                     # Install dependencies (frozen lockfile)
npm run dev               # Start development server (tsx watch)
npm test                  # Run Vitest tests with coverage
npm run lint              # ESLint check
npm run type-check        # TypeScript type checking
npm run build             # Build production bundle
npm run test:watch        # Run tests in watch mode
npm run test:coverage     # Generate detailed coverage report
```

#### Python Services (Research, Brand, Content, Agent)
```bash
cd plasma-engine-[service]
pip install -e .          # Install from pyproject.toml
pip install -r requirements-dev.txt  # Install dev dependencies

# Running
uvicorn app.main:app --reload        # Research service (default port 8000)
uvicorn app.main:app --reload --port 800X  # Other services (check Makefile for ports)

# Testing
pytest                    # Run all tests
pytest tests/test_health.py -v  # Run specific test file
pytest -m unit           # Run only unit tests
pytest -m "not slow"     # Skip slow tests
pytest --cov=app         # Run with coverage

# Linting & Formatting
black .                  # Format code
ruff check .            # Lint code
mypy app/               # Type checking
```

### Running Individual Tests
```bash
# Python services
pytest tests/test_health.py::test_health_endpoint_reports_ok_status -v
pytest -m unit              # Run only unit tests
pytest -m "not slow"        # Skip slow tests
pytest -m "not external"    # Skip external dependency tests

# TypeScript services
npm test -- tests/health.test.ts
npm run test:watch          # Run tests in watch mode
```

### Scraper Testing Commands
```bash
# BrightData scrapers
python scripts/test_brightdata_scrapers.py
python scripts/test_brightdata_social.py   # Social media scrapers
python scripts/test_scrapers_live.py       # Live API testing

# ScraperAPI testing
python scripts/test_scraperapi.py
python scripts/test_scraperapi_quick.py    # Quick validation

# Manual scraper testing
./test_scraper_manual.sh [url]
```

## High-Level Architecture

### Service Communication Flow
```
External Clients
       ↓
Gateway (Apollo GraphQL Federation)
       ↓
[Research | Brand | Content | Agent] Services
       ↓
Shared Infrastructure (PostgreSQL, Redis, Neo4j)
```

### Service Stack & Responsibilities

1. **Gateway** (`plasma-engine-gateway`) - TypeScript, Express, Apollo Server
   - API gateway and GraphQL federation
   - Authentication & authorization middleware
   - Request routing and aggregation
   - Entry point on port 3000

2. **Research** (`plasma-engine-research`) - Python, FastAPI, Neo4j
   - GraphRAG system for knowledge management
   - Vector search and semantic retrieval
   - Document processing and indexing
   - Runs on port 8000

3. **Brand** (`plasma-engine-brand`) - Python, FastAPI
   - Brand monitoring and sentiment analysis
   - Social media tracking
   - Analytics and reporting
   - Runs on port 8001

4. **Content** (`plasma-engine-content`) - Python, FastAPI
   - AI-powered content generation
   - Publishing workflows and scheduling
   - Voice and tone compliance
   - Runs on port 8002

5. **Agent** (`plasma-engine-agent`) - Python, FastAPI
   - Multi-agent orchestration
   - MCP (Model Context Protocol) support
   - Browser automation via Playwright
   - Runs on port 8003

### Data Architecture

- **Database Isolation**: Each service maintains its own PostgreSQL database
- **Knowledge Graph**: Research service uses Neo4j for relationships
- **Caching**: Shared Redis for session management and caching
- **Background Tasks**: Celery + Redis for async processing
- **Vector Storage**: pgvector for embeddings (Research service)

### AI/ML Integration Patterns

- **Research Service**: LangChain, LlamaIndex for RAG workflows
- **Content Service**: OpenAI/Anthropic APIs for text generation
- **Brand Service**: Transformers, spaCy for NLP analysis
- **Agent Service**: Multi-agent coordination with tool calling

## Development Workflow

### Feature Development
1. Create feature branch from `develop`
2. Make changes in appropriate service directory
3. Run service-specific tests and linting
4. Ensure CI passes (triggered on PR)
5. Request CodeRabbit and human review

### CI/CD Pipeline (GitHub Actions)
- **Triggered on**: Push to main/develop, all PRs
- **Checks**: Linting, type checking, unit tests, security scanning
- **Coverage Requirements**: 90% minimum
- **Security**: Bandit (Python), npm audit (Node), Snyk scanning
- **Docker**: Images built and pushed on main branch merges

### Testing Strategy
- **Python Services**: pytest with async support, fixtures for mocking
- **TypeScript Services**: Vitest for unit/integration tests
- **Test Markers**: `unit`, `integration`, `slow`, `external`, `db`, `ai`
- **Coverage Target**: 90% across all services

## Environment Configuration

Each service requires a `.env` file (copy from `.env.example`). Key variables:
- Database URLs: `DATABASE_URL`, `REDIS_URL`, `NEO4J_URI`
- AI APIs: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- Auth: `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`
- Service URLs: `GATEWAY_URL`, internal service endpoints

## Common Operations

### Debugging Service Issues
```bash
# Check if infrastructure is running
make ps
docker ps                  # Alternative: view Docker containers directly

# View logs for all infrastructure services
make logs
docker-compose -f docker-compose.infrastructure.yml logs -f

# Restart a specific service
cd plasma-engine-[service] && [restart command]

# Check database connectivity
docker exec -it plasma-engine-postgres psql -U postgres -d plasma_[service]

# Check Redis connectivity
docker exec -it plasma-engine-redis redis-cli ping

# Check Neo4j browser
open http://localhost:7474  # Neo4j browser interface
```

### Dependency Management
```bash
# Python services
pip-compile requirements.in  # Generate locked requirements
pip install -r requirements.txt
pip install -e .            # Install service in editable mode from pyproject.toml

# TypeScript services
npm update  # Update within semver ranges
npm ci      # Clean install from lock file
```

### Repository Synchronization
```bash
make pull-all        # Pull latest for all repos
make status-all      # Check git status across all repos
make sync-templates  # Sync shared templates from plasma-engine-shared
```

## Web Scraping Infrastructure

### BrightData Integration
- Configuration: `brightdata-mcp-config.json`
- Test results: `brightdata_*_results.json` files
- Scripts in `scripts/` for testing various scraper types
- Supports social media scraping (Twitter/X, LinkedIn, etc.)

### ScraperAPI Integration
- Quick validation available via test scripts
- Supports general web scraping with proxy rotation
- Rate limiting and retry logic built-in

### Automation & CI/CD
- GitHub Actions workflows in `.github/workflows/`
- Autopilot dispatcher for automated issue management: `scripts/automation/autopilot_dispatcher.py`
- CodeRabbit integration for automated PR reviews

## Important Project Files

### Configuration
- `.env.example` - Template for environment variables (copy to `.env`)
- `pytest.ini` - Global pytest configuration with markers and coverage settings
- `docker-compose.infrastructure.yml` - Infrastructure services setup
- `.coderabbit.yaml` - Automated code review configuration

### Documentation
- `docs/` - Comprehensive documentation including:
  - API reference and OpenAPI specs
  - Architecture diagrams and ADRs
  - Deployment guides
  - Scraper documentation
  - Troubleshooting guides

### Scripts
- `scripts/` - Utility scripts for:
  - Scraper testing (BrightData, ScraperAPI)
  - GitHub automation and issue creation
  - Database initialization
  - Build and lint automation
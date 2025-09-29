# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Plasma Engine** is an enterprise AI platform organized as a multi-repository microservices architecture. The platform spans research automation, brand monitoring, content orchestration, and agent workflows. This parent repository coordinates 7 service repositories under a single organization.

## Multi-Repository Architecture

The organization uses a multi-repo structure (ADR-0001) with separate repositories for each domain:

| Repository | Purpose | Stack | Port |
|------------|---------|-------|------|
| `plasma-engine-gateway` | GraphQL Federation, Auth, API Gateway | TypeScript, Apollo Server | 3000 |
| `plasma-engine-research` | Parallel search, GraphRAG, knowledge ingestion | Python, FastAPI, Neo4j | 8000 |
| `plasma-engine-brand` | Brand monitoring, social analytics, sentiment | Python, FastAPI, ETL | 8001 |
| `plasma-engine-content` | Content planning, AI generation, publishing | Python, FastAPI | 8002 |
| `plasma-engine-agent` | Workflow builder, agent orchestration, MCP | Python, FastAPI | 8003 |
| `plasma-engine-shared` | Shared libraries, templates, tooling | Python + TypeScript packages | - |
| `plasma-engine-infra` | Terraform, Helm, Docker Compose, CI workflows | HCL, YAML | - |

**Key Insight**: Services are loosely coupled and can be deployed independently. The Gateway provides unified GraphQL federation over all backend services.

## Essential Commands

### Multi-Repository Management

```bash
# Clone all repositories
make clone-all

# Pull latest changes from all repos
make pull-all

# Check git status across all repos
make status-all

# Complete development environment setup
make setup
```

### Service Development

**Python Services** (research, brand, content, agent):
```bash
# Run development server (from service directory)
uvicorn app.main:app --reload --port <PORT>

# Run tests with coverage (requires 90%)
pytest tests/ --cov=app --cov-report=term-missing

# Lint and type check
ruff check .
black --check .
mypy app/ --ignore-missing-imports

# Install dependencies
pip install -e .
pip install -e ".[dev]"
```

**TypeScript Services** (gateway):
```bash
# Run development server
npm run dev

# Run tests with coverage
npm test
npm run test:coverage

# Lint and type check
npm run lint
npm run type-check

# Build for production
npm run build
```

### Run All Services

```bash
# Start infrastructure (PostgreSQL, Redis, Neo4j, MinIO)
make start-infra

# Run all services in tmux session
make run-all

# Or run individual services
make run-gateway    # Port 3000
make run-research   # Port 8000
make run-brand      # Port 8001
make run-content    # Port 8002
make run-agent      # Port 8003
```

### Testing

```bash
# Test all services
make test-all

# Test specific Python service
cd plasma-engine-<service> && pytest

# Test specific TypeScript service
cd plasma-engine-gateway && npm test

# Lint all services
make lint-all
```

### Database Management

```bash
# Initialize all databases
make init-db

# Creates the following databases:
# - plasma_engine (gateway)
# - plasma_research
# - plasma_brand
# - plasma_content
# - plasma_agent
```

### Docker Operations

```bash
# Build all Docker images
make build-all

# Show infrastructure logs
make logs

# Show running services
make ps

# Stop infrastructure
make stop-infra

# Clean build artifacts
make clean
```

## Tech Stack Standards (ADR-0002)

### Backend Services
- **Language**: Python 3.11+
- **Framework**: FastAPI with SQLModel
- **Async**: Built-in asyncio, Celery/Prefect for orchestration
- **Databases**: PostgreSQL (relational), Redis (cache/queue), Neo4j (knowledge graph)
- **Testing**: pytest with 90% coverage requirement

### Frontend/Gateway
- **Language**: TypeScript 5.x
- **Runtime**: Node.js ≥ 20.10.0
- **Gateway**: Apollo Server 4.x with Federation
- **Testing**: Vitest with coverage reporting

### AI Integration
- **SDK**: `ai` SDK wrappers in `plasma-engine-shared`
- **Models**: OpenAI (gpt-5, gpt-5-mini, gpt-5-nano), Anthropic (claude-3-7-sonnet), Gemini (gemini-1.5-pro)

### Infrastructure
- **Local**: Docker Compose
- **Production**: Kubernetes with Helm charts
- **IaC**: Terraform for cloud provisioning
- **Observability**: OpenTelemetry, Prometheus, Grafana, Loki, Sentry

## Code Quality Standards

### Python
- **Formatter**: black (line-length=100)
- **Linter**: ruff (strict mode)
- **Type Checker**: mypy with strict settings
- **Test Runner**: pytest with asyncio, coverage, benchmark plugins
- **Coverage**: 90% minimum (enforced in CI)

### TypeScript
- **Formatter**: prettier
- **Linter**: eslint with @typescript-eslint/strict
- **Test Runner**: vitest with coverage
- **Type Checking**: TypeScript strict mode enabled

## Testing Patterns

### Python Unit Tests
- Located in `tests/` directory
- Naming: `test_*.py` for files, `test_*` for functions
- Use `pytest.mark` decorators: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- FastAPI tests use `httpx.AsyncClient` with `TestClient`
- Example:
  ```python
  @pytest.mark.asyncio
  async def test_health_endpoint(client):
      response = await client.get("/health")
      assert response.status_code == 200
  ```

### TypeScript Unit Tests
- Located alongside source or in `__tests__/` directories
- Use vitest with supertest for API testing
- Coverage exported to Codecov via CI
- Example:
  ```typescript
  describe("Health Endpoint", () => {
    it("returns 200 OK", async () => {
      const response = await request(app).get("/health");
      expect(response.status).toBe(200);
    });
  });
  ```

## GraphQL Federation Architecture

The `plasma-engine-gateway` uses Apollo Federation to compose subgraphs from backend services:

```
Client → Gateway (Apollo Gateway) → [Research|Brand|Content|Agent] Subgraphs
```

- Each backend service exposes a GraphQL subgraph endpoint
- Gateway handles schema composition, query planning, and authentication
- Use `@key`, `@external`, `@requires` directives for entity federation
- Gateway provides unified `__typename` and introspection

## CI/CD Pipeline

GitHub Actions workflows located in `.github/workflows/`:

### Main Pipeline (`ci.yml`)
1. **Lint**: Parallel linting for Python (ruff, black, mypy) and TypeScript (eslint)
2. **Security**: Snyk scanning, Bandit (Python), npm audit
3. **Unit Tests**: Matrix testing per service with PostgreSQL/Redis services
4. **Integration Tests**: Docker Compose smoke tests for all health endpoints
5. **Build**: Docker images pushed to GitHub Container Registry (main branch only)
6. **Deploy**: Automatic staging deployment on main branch

### Coverage Requirements
- Python: 90% minimum (enforced via pytest-cov)
- TypeScript: Coverage uploaded to Codecov
- CI fails if coverage drops below threshold

## Environment Variables

Standard environment variable naming (see `.env.example` in each service):

```bash
# AI Providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=

# Databases
POSTGRES_URL=postgresql://plasma:plasma@localhost:5432/plasma_<service>
REDIS_URL=redis://localhost:6379/0
NEO4J_URI=bolt://localhost:7687

# GitHub Integration
GITHUB_TOKEN=

# Service Configuration
PORT=<service-specific-port>
LOG_LEVEL=info
DEBUG=false
```

**Important**: Never commit secrets. Use `.env` files locally and GitHub Secrets for CI.

## Development Workflow

1. **Branch Naming**: `<service>/<ISSUE-ID>-description` (e.g., `gateway/PE-42-add-auth`)
2. **Commits**: Use Conventional Commits format (`feat:`, `fix:`, `chore:`, etc.)
3. **Pre-commit**: Run `make lint` and `make test` before pushing
4. **PRs**: Must pass CI, security scans, and CodeRabbit review
5. **Approval**: At least one human reviewer required
6. **Merge**: Squash and merge to main branch

## Troubleshooting

### Port Conflicts
If services fail to start, check for port conflicts:
```bash
# Check what's using a port
lsof -i :<PORT>

# Kill process on port
kill -9 $(lsof -t -i:<PORT>)
```

### Docker Database Issues
```bash
# Reset Docker infrastructure
make stop-infra
docker volume prune
make start-infra

# Reinitialize databases
make init-db
```

### Python Dependency Issues
```bash
# Clean and reinstall
cd plasma-engine-<service>
rm -rf .venv __pycache__ .pytest_cache
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### TypeScript Dependency Issues
```bash
# Clean and reinstall
cd plasma-engine-gateway
rm -rf node_modules package-lock.json
npm install
```

## Documentation

- **ADRs**: Architecture Decision Records in `docs/adrs/`
- **Tickets**: Phase planning in `docs/tickets/`
- **API Docs**: Service-specific docs in each repository's README
- **Handbook**: Development standards in `plasma-engine-shared/docs/development-handbook.md`

## Claude Code + CodeRabbit Integration

### Automatic Code Review & Implementation Loop

The repository has an automated workflow where CodeRabbit and Claude Code work together:

1. **CodeRabbit Reviews PRs**: CodeRabbit automatically reviews all pull requests and provides feedback
2. **CodeRabbit Tags Claude**: When CodeRabbit suggests changes, it tags `@claude` in its comments
3. **Claude Implements Changes**: Claude Code automatically:
   - Reads and analyzes CodeRabbit's suggestions
   - Implements all suggested improvements
   - Runs tests to verify changes
   - Commits changes with descriptive messages
   - Replies to CodeRabbit confirming implementation

### How It Works

**Workflow File**: `.github/workflows/claude-code.yml`

**Triggers**:
- When `@claude` is mentioned in any PR comment
- When CodeRabbit (coderabbitai[bot]) leaves a review comment
- When a PR is opened or updated (for automated review)

**What Claude Does**:
- **For CodeRabbit Comments**: Automatically implements all suggestions related to code quality, security, and performance
- **For @claude Mentions**: Responds to user requests in PR comments
- **For New PRs**: Provides automated code review feedback

**CodeRabbit Configuration**: All `.coderabbit.yaml` files are configured to tag `@claude` when suggesting code changes.

### Manual Invocation

You can manually trigger Claude Code in any PR by commenting:
```
@claude [your request]
```

Examples:
- `@claude please implement the changes suggested by CodeRabbit`
- `@claude add unit tests for the new authentication flow`
- `@claude refactor this code to improve performance`

### Required Secrets

Make sure these GitHub secrets are configured:
- `ANTHROPIC_API_KEY` - Your Anthropic API key for Claude Code
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

### Permissions

The Claude Code workflow has permissions to:
- Read repository contents
- Write to pull requests
- Create and edit comments
- Commit code changes

## Key Architectural Patterns

1. **Service Isolation**: Each service has its own database and can be deployed independently
2. **GraphQL Federation**: Gateway composes unified API from multiple subgraphs
3. **Async-First**: Python services use FastAPI with async/await patterns
4. **Event-Driven**: Redis for pub/sub and job queues (Celery/Prefect)
5. **Knowledge Graph**: Neo4j for research relationships and entity linking
6. **Observability**: OpenTelemetry tracing across all services
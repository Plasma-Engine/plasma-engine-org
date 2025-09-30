# Plasma Engine Content Service

FastAPI-based content generation service with LangChain integration for AI-powered content creation.

## Features

- **Content Generation**: AI-powered content creation using LangChain
- **Async Processing**: Handles multiple content generation requests concurrently
- **LLM Integration**: Configurable LLM clients (OpenAI, Anthropic, etc.)
- **RESTful API**: Clean API design with FastAPI
- **Content Models**: Structured content schemas and validation

## Tech Stack

- **FastAPI**: Modern Python web framework
- **LangChain**: LLM orchestration and chain management
- **SQLModel**: Database ORM with Pydantic integration
- **Celery**: Async task processing for long-running generation jobs
- **Redis**: Caching and queue management

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Run the service
uvicorn src.main:app --reload --port 8003

# Or using Docker
docker-compose up
```

## API Endpoints

### Content Generation
- `POST /api/v1/content/generate` - Generate new content
- `GET /api/v1/content/{content_id}` - Retrieve generated content
- `GET /api/v1/content/status/{job_id}` - Check generation job status

### Templates
- `GET /api/v1/templates` - List content templates
- `POST /api/v1/templates` - Create new template
- `PUT /api/v1/templates/{template_id}` - Update template

### Health
- `GET /health` - Service health check
- `GET /health/ready` - Readiness probe

## Environment Variables

```env
# LLM Configuration
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
DEFAULT_MODEL=gpt-4-turbo-preview

# Database
DATABASE_URL=postgresql://user:pass@localhost/content_db

# Redis
REDIS_URL=redis://localhost:6379

# Service Config
SERVICE_PORT=8003
LOG_LEVEL=info
```

## Project Structure

```
content-service/
├── src/
│   ├── api/              # API routes and endpoints
│   ├── chains/           # LangChain chains and prompts
│   ├── clients/          # LLM client configurations
│   ├── core/             # Core configuration and settings
│   ├── models/           # SQLModel database models
│   ├── schemas/          # Pydantic schemas for validation
│   ├── services/         # Business logic and services
│   └── main.py           # FastAPI application entry point
├── tests/                # Test suite
├── docs/                 # Additional documentation
├── Dockerfile            # Container definition
├── docker-compose.yml    # Local development stack
└── requirements.txt      # Python dependencies
```

## Development

```bash
# Run tests
pytest

# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/
```

## Architecture

The service follows a clean architecture pattern:
- **API Layer**: FastAPI routes handle HTTP requests
- **Service Layer**: Business logic and LangChain orchestration
- **Repository Layer**: Data access through SQLModel
- **External Clients**: LLM providers via LangChain

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_content_generation.py
```

## Deployment

The service is containerized and can be deployed to any Kubernetes cluster or container platform.

```bash
# Build Docker image
docker build -t plasma-engine-content:latest .

# Push to registry
docker push your-registry/plasma-engine-content:latest
```
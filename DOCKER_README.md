# 🐳 Docker Development Environment

This repository includes a complete Docker Compose setup for local development of the Plasma Engine platform.

## Quick Start

```bash
# One-command setup
./scripts/dev.sh setup

# Or using Make
make setup
```

## What's Included

### Application Services
- **Gateway** (Port 8000) - API Gateway with FastAPI
- **Research** (Port 8001) - Research service with GraphRAG
- **Brand** (Port 8002) - Brand monitoring service
- **Content** (Port 3000) - Content generation UI (Next.js)
- **Agent** (Port 3001) - Agent orchestration UI (Next.js)

### Infrastructure
- **PostgreSQL** - Primary database
- **Redis** - Caching and Celery backend
- **Neo4j** - Graph database for research
- **RabbitMQ** - Message queue for async tasks
- **Elasticsearch** - Full-text search
- **MinIO** - S3-compatible object storage

### Development Tools
- **Adminer** - Database management UI
- **Flower** - Celery monitoring
- **Kibana** - Elasticsearch UI
- **MailHog** - Email testing

## File Structure

```
.
├── docker-compose.yml           # Main services configuration
├── docker-compose.override.yml  # Development overrides
├── .env.example                 # Environment variables template
├── docker/
│   ├── python.Dockerfile.dev   # Python service template
│   └── node.Dockerfile.dev     # Node.js service template
├── scripts/
│   ├── dev.sh                  # Development helper script
│   └── db/
│       └── init/               # Database initialization
│           ├── 01-create-databases.sql
│           └── 02-seed-data.sql
└── docs/
    ├── ONBOARDING.md           # New developer guide
    └── development/
        └── LOCAL_SETUP.md      # Detailed setup instructions
```

## Common Commands

### Using the dev script:
```bash
./scripts/dev.sh start    # Start all services
./scripts/dev.sh stop     # Stop all services
./scripts/dev.sh status   # Check service health
./scripts/dev.sh logs     # View logs
./scripts/dev.sh urls     # Show service URLs
```

### Using Make:
```bash
make up           # Start services
make down         # Stop services
make restart      # Restart services
make ps           # Show running services
make logs         # View logs
make health       # Check health
```

### Database Operations:
```bash
make db-migrate   # Run migrations
make db-reset     # Reset databases
make db-backup    # Create backup
make db-seed      # Load sample data
```

## Environment Configuration

1. Copy `.env.example` to `.env`
2. Update any necessary values
3. Most defaults work for local development

Key variables:
- Service ports (if you have conflicts)
- API keys (optional for basic dev)
- Database credentials

## Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Content UI | http://localhost:3000 | user@plasma.dev / password123 |
| Gateway API | http://localhost:8000/docs | - |
| Adminer | http://localhost:8080 | plasma / plasma_dev |
| RabbitMQ | http://localhost:15672 | plasma / rabbit_dev |
| Neo4j | http://localhost:7474 | neo4j / neo4j_dev |
| Flower | http://localhost:5555 | admin / admin |
| MinIO | http://localhost:9001 | minioadmin / minioadmin |
| MailHog | http://localhost:8025 | - |

## Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker info

# Reset everything
./scripts/dev.sh cleanup
./scripts/dev.sh setup
```

### Port conflicts
Edit `.env` file to change port numbers

### Performance issues
- Increase Docker Desktop memory allocation
- Use `make up-minimal` for core services only

## Development Workflow

1. **Start services**: `make up`
2. **Write code** - Hot reload is enabled
3. **View logs**: `make logs-gateway`
4. **Run tests**: `make test`
5. **Stop services**: `make down`

## Getting Help

- Check [LOCAL_SETUP.md](docs/development/LOCAL_SETUP.md) for detailed instructions
- Review [ONBOARDING.md](docs/ONBOARDING.md) for new developers
- Run `make help` to see all available commands

## Notes

- All services include hot reload for development
- Data persists in Docker volumes between restarts
- Use `./scripts/dev.sh reset-db` to clear all data
- Celery workers start automatically for async tasks
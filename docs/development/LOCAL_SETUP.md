# Plasma Engine Local Development Setup

This guide will help you set up the Plasma Engine platform for local development.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Service Architecture](#service-architecture)
- [Development Workflow](#development-workflow)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)
- [IDE Configuration](#ide-configuration)

## Prerequisites

### Required Software

- **Docker Desktop** (v4.x or later)
  - [Download for Mac](https://docs.docker.com/desktop/mac/install/)
  - [Download for Windows](https://docs.docker.com/desktop/windows/install/)
  - [Download for Linux](https://docs.docker.com/desktop/linux/install/)

- **Docker Compose** (v2.x or later) - Usually included with Docker Desktop

- **Git** (v2.x or later)
  - [Download Git](https://git-scm.com/downloads)

### Recommended Software

- **Make** - For running Makefile commands
  - Mac: `brew install make`
  - Ubuntu/Debian: `sudo apt-get install make`
  - Windows: Use WSL2 or Git Bash

- **Node.js** (v20.x) and **Python** (v3.11) - For local development without Docker
  - [Node.js Download](https://nodejs.org/)
  - [Python Download](https://www.python.org/downloads/)

### System Requirements

- **RAM**: Minimum 8GB, recommended 16GB
- **Storage**: At least 20GB free space
- **CPU**: 4+ cores recommended

## Quick Start

For experienced developers who want to get up and running quickly:

```bash
# 1. Clone the repository
git clone https://github.com/plasma-engine/plasma-engine-org.git
cd plasma-engine-org

# 2. Run the setup script
chmod +x scripts/dev.sh
./scripts/dev.sh setup

# 3. Access the services
open http://localhost:3000  # Content UI
open http://localhost:8000  # Gateway API
```

Default credentials:
- **Admin**: admin@plasma.dev / password123
- **User**: user@plasma.dev / password123

## Detailed Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/plasma-engine/plasma-engine-org.git
cd plasma-engine-org
```

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred editor
# Most defaults work out of the box for local development
vim .env
```

Key environment variables to review:

- `JWT_SECRET` - Change for production
- API keys for external services (optional for basic development)
- Port numbers if you have conflicts

### Step 3: Start Infrastructure Services

```bash
# Start only infrastructure services first
docker-compose up -d postgres redis neo4j rabbitmq

# Check that they're healthy
docker-compose ps

# View logs if needed
docker-compose logs -f postgres
```

### Step 4: Initialize Databases

The databases are automatically initialized with the SQL scripts in `scripts/db/init/`.
These create:
- All required databases
- Extensions (UUID, crypto, full-text search, vector)
- Initial schema
- Seed data for development

### Step 5: Start Application Services

```bash
# Build and start all application services
docker-compose up -d

# Or start specific services
docker-compose up -d gateway research

# Monitor startup
docker-compose logs -f
```

### Step 6: Verify Installation

```bash
# Check service health
./scripts/dev.sh status

# Run basic health checks
curl http://localhost:8000/health  # Gateway
curl http://localhost:8001/health  # Research
curl http://localhost:8002/health  # Brand
curl http://localhost:3000/api/health  # Content
curl http://localhost:3001/api/health  # Agent
```

## Service Architecture

### Core Services

| Service | Port | Technology | Purpose |
|---------|------|------------|---------|
| Gateway | 8000 | Python/FastAPI | API gateway, authentication, GraphQL federation |
| Research | 8001 | Python/FastAPI | Research engine, GraphRAG, knowledge management |
| Brand | 8002 | Python/FastAPI | Brand monitoring, social analytics |
| Content | 3000 | TypeScript/Next.js | Content generation UI and API |
| Agent | 3001 | TypeScript/Next.js | Agent orchestration UI and runtime |

### Infrastructure Services

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5432 | Primary database for all services |
| Redis | 6379 | Caching, session storage, Celery backend |
| Neo4j | 7474/7687 | Graph database for research service |
| RabbitMQ | 5672/15672 | Message queue for async tasks |
| Elasticsearch | 9200 | Full-text search and analytics |
| MinIO | 9000/9001 | S3-compatible object storage |

### Development Tools

| Tool | Port | Purpose | Credentials |
|------|------|---------|-------------|
| Adminer | 8080 | Database UI | Use postgres credentials |
| RabbitMQ Management | 15672 | Queue monitoring | plasma / rabbit_dev |
| Neo4j Browser | 7474 | Graph database UI | neo4j / neo4j_dev |
| Flower | 5555 | Celery monitoring | admin / admin |
| MinIO Console | 9001 | Object storage UI | minioadmin / minioadmin |
| Kibana | 5601 | Elasticsearch UI | No auth required |
| MailHog | 8025 | Email testing | No auth required |

## Development Workflow

### Daily Development

1. **Start services**:
   ```bash
   ./scripts/dev.sh start
   ```

2. **Monitor logs**:
   ```bash
   # All services
   ./scripts/dev.sh logs

   # Specific service
   ./scripts/dev.sh logs gateway
   ```

3. **Make changes**: Edit code in your IDE - hot reload is enabled

4. **Run tests**:
   ```bash
   ./scripts/dev.sh test
   ```

5. **Stop services**:
   ```bash
   ./scripts/dev.sh stop
   ```

### Working with Individual Services

```bash
# Execute commands in a container
./scripts/dev.sh exec gateway bash
./scripts/dev.sh exec research python manage.py shell

# Run service-specific commands
docker-compose exec gateway alembic upgrade head  # Run migrations
docker-compose exec research pytest  # Run tests
docker-compose exec content npm run build  # Build frontend
```

### Database Management

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U plasma -d plasma_engine

# Run migrations
./scripts/dev.sh migrate

# Reset databases (WARNING: destroys all data)
./scripts/dev.sh reset-db

# Backup database
docker-compose exec postgres pg_dump -U plasma plasma_engine > backup.sql

# Restore database
docker-compose exec -T postgres psql -U plasma plasma_engine < backup.sql
```

## Common Tasks

### Adding Dependencies

**Python services**:
```bash
# Add to requirements.txt, then:
docker-compose exec gateway pip install -r requirements.txt
```

**Node.js services**:
```bash
# Add to package.json, then:
docker-compose exec content npm install
```

### Running Celery Workers

```bash
# Start worker (already in docker-compose.override.yml)
docker-compose up -d research-worker

# Monitor tasks
open http://localhost:5555  # Flower UI
```

### Debugging

**Python services**:
```python
# Add breakpoint in code
import ipdb; ipdb.set_trace()

# Run service with stdin
docker-compose run --rm gateway
```

**Node.js services**:
```javascript
// Add debugger statement
debugger;

// Connect Chrome DevTools to port 9229/9230
```

### Creating New Services

1. Create service directory:
   ```bash
   mkdir plasma-engine-newservice
   ```

2. Add to docker-compose.yml

3. Create Dockerfile.dev based on templates in `docker/`

4. Update Makefile and scripts/dev.sh

## Troubleshooting

### Common Issues

**Port already in use**:
```bash
# Find process using port
lsof -i :8000

# Change port in .env file
GATEWAY_PORT=8001
```

**Container won't start**:
```bash
# Check logs
docker-compose logs gateway

# Rebuild image
docker-compose build --no-cache gateway

# Remove volumes and restart
docker-compose down -v
docker-compose up -d
```

**Database connection errors**:
```bash
# Ensure postgres is healthy
docker-compose ps postgres

# Check connection string
docker-compose exec gateway env | grep DATABASE_URL

# Test connection
docker-compose exec postgres pg_isready
```

**Permission errors**:
```bash
# Fix file permissions
sudo chown -R $(whoami):$(whoami) .

# On Linux, add user to docker group
sudo usermod -aG docker $USER
```

### Performance Issues

**Slow performance on Mac/Windows**:
- Increase Docker Desktop memory allocation (Settings > Resources)
- Use named volumes instead of bind mounts for node_modules
- Consider using Docker Desktop's new virtualization framework

**High memory usage**:
```bash
# Check resource usage
docker stats

# Limit service resources in docker-compose.yml
services:
  gateway:
    mem_limit: 512m
```

### Resetting Everything

```bash
# Nuclear option - removes everything
./scripts/dev.sh cleanup

# Start fresh
./scripts/dev.sh setup
```

## IDE Configuration

### VS Code

Recommended extensions:
- Python
- Pylance
- Docker
- ESLint
- Prettier
- Thunder Client (API testing)

Settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "/usr/local/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

### PyCharm

1. Configure Docker interpreter:
   - Settings > Project > Python Interpreter
   - Add > Docker Compose
   - Select service (e.g., gateway)

2. Enable Django/FastAPI support:
   - Settings > Languages & Frameworks > Django/FastAPI

### Remote Development

For better performance, consider:
- VS Code Remote Containers
- GitHub Codespaces
- GitPod

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Celery Documentation](https://docs.celeryproject.org/)

## Getting Help

- Check the [Troubleshooting](#troubleshooting) section
- Review service logs: `./scripts/dev.sh logs [service]`
- Create an issue on GitHub
- Check service-specific README files in each repository

## Next Steps

Once your local environment is running:

1. Explore the API documentation:
   - Gateway: http://localhost:8000/docs
   - Research: http://localhost:8001/docs
   - Brand: http://localhost:8002/docs

2. Try the example workflows in `docs/examples/`

3. Review the architecture documentation in `docs/architecture/`

4. Start building!
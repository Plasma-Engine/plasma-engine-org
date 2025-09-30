# Plasma Engine - Development Environment Setup

This guide will help you set up the complete Plasma Engine development environment on your local machine.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

### Required
- **Docker Desktop** (v4.0+) - [Download here](https://www.docker.com/products/docker-desktop)
- **Docker Compose** (v2.0+) - Usually included with Docker Desktop
- **Git** (v2.30+) - For version control

### Optional but Recommended
- **Node.js** (v18+) - For local gateway development
- **Python** (3.11+) - For local service development
- **Make** - For using Makefile commands
- **curl** - For health checks

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Plasma-Engine/plasma-engine-org.git
cd plasma-engine-org
```

### 2. Start Development Environment
```bash
./scripts/dev-start.sh
```

This script will:
- ✅ Check prerequisites
- ✅ Create `.env` file with defaults
- ✅ Start infrastructure services (PostgreSQL, Redis, Neo4j)
- ✅ Initialize databases
- ✅ Install dependencies
- ✅ Start all application services

### 3. Verify Everything is Running
```bash
./scripts/dev-status.sh
```

## 🏗️ Architecture Overview

The development environment consists of:

### Infrastructure Services
- **PostgreSQL** (port 5432) - Primary database
- **Redis** (port 6379) - Cache and message queue  
- **Neo4j** (ports 7474/7687) - Graph database for research service
- **pgAdmin** (port 5050) - Database administration

### Application Services
- **Gateway** (port 3000) - GraphQL federation gateway
- **Research** (port 8000) - RAG and knowledge management
- **Brand** (port 8001) - Brand monitoring and analytics
- **Content** (port 8002) - Content generation and publishing
- **Agent** (port 8003) - Multi-agent orchestration

## 🔧 Configuration

### Environment Variables
The development environment uses a `.env` file for configuration. The startup script creates one with defaults:

```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=plasma_engine

# Redis Configuration  
REDIS_PASSWORD=redis

# Neo4j Configuration
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password

# AI API Keys (Optional)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

**Important**: Add your actual API keys to the `.env` file for AI features to work.

### Service Configuration
Each service has its own configuration files:
- `plasma-engine-gateway/package.json` - Gateway dependencies
- `plasma-engine-research/pyproject.toml` - Research service dependencies
- `plasma-engine-brand/requirements.txt` - Brand service dependencies
- `plasma-engine-content/requirements.txt` - Content service dependencies
- `plasma-engine-agent/requirements.txt` - Agent service dependencies

## 📊 Service URLs

Once running, services are available at:

| Service | URL | Description |
|---------|-----|-------------|
| Gateway | http://localhost:3000 | GraphQL API endpoint |
| Research | http://localhost:8000 | Research service API |
| Brand | http://localhost:8001 | Brand monitoring API |
| Content | http://localhost:8002 | Content generation API |
| Agent | http://localhost:8003 | Agent orchestration API |
| pgAdmin | http://localhost:5050 | Database admin interface |
| Neo4j Browser | http://localhost:7474 | Graph database browser |

## 🛠️ Management Scripts

### Start Services
```bash
./scripts/dev-start.sh
```

### Stop Services
```bash
./scripts/dev-stop.sh
```

### Stop and Clean All Data
```bash
./scripts/dev-stop.sh --clean
```

### Check Status
```bash
./scripts/dev-status.sh
```

## 🐳 Docker Commands

### View Running Services
```bash
docker-compose ps
```

### View Service Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f research
```

### Restart a Service
```bash
docker-compose restart gateway
```

### Access Service Shell
```bash
# Python services
docker-compose exec research /bin/bash

# Node.js services  
docker-compose exec gateway /bin/bash
```

### Rebuild Service
```bash
docker-compose build research
docker-compose up -d research
```

## 🗄️ Database Access

### PostgreSQL
- **Host**: localhost:5432
- **Username**: postgres
- **Password**: postgres
- **Databases**: plasma_gateway, plasma_research, plasma_brand, plasma_content, plasma_agent

### Redis
- **Host**: localhost:6379
- **Password**: redis

### Neo4j
- **Browser**: http://localhost:7474
- **Bolt**: bolt://localhost:7687
- **Username**: neo4j
- **Password**: neo4j_password

## 🧪 Development Workflow

### Local Development
1. Make code changes in service directories
2. Services with volume mounts will auto-reload
3. Use `docker-compose restart <service>` if needed

### Testing
```bash
# Run tests for a specific service
cd plasma-engine-research
pytest

# Run tests in container
docker-compose exec research pytest
```

### Debugging
```bash
# View service logs
docker-compose logs -f research

# Access service shell
docker-compose exec research /bin/bash

# Check service health
curl http://localhost:8000/health
```

## 🚨 Troubleshooting

### Common Issues

#### Docker Daemon Not Running
```bash
# Error: Cannot connect to the Docker daemon
# Solution: Start Docker Desktop
```

#### Port Already in Use
```bash
# Error: Port 5432 is already allocated
# Solution: Stop conflicting services or change ports in docker-compose.yml
```

#### Service Won't Start
```bash
# Check logs
docker-compose logs service-name

# Rebuild service
docker-compose build service-name
docker-compose up -d service-name
```

#### Database Connection Issues
```bash
# Wait for PostgreSQL to be ready
docker-compose exec postgres pg_isready -U postgres

# Recreate databases
docker-compose exec postgres psql -U postgres -c "DROP DATABASE plasma_research;"
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE plasma_research;"
```

### Reset Everything
```bash
# Stop all services and remove data
./scripts/dev-stop.sh --clean

# Start fresh
./scripts/dev-start.sh
```

## 📝 Development Tips

### Code Formatting
```bash
# Python services
cd plasma-engine-research
black .
ruff check .

# Node.js services  
cd plasma-engine-gateway
npm run lint
npm run format
```

### Performance Monitoring
```bash
# Monitor resource usage
docker stats

# Monitor specific service
docker stats plasma-research
```

### Database Migrations
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d plasma_research

# Run custom SQL
docker-compose exec postgres psql -U postgres -d plasma_research -c "SELECT * FROM your_table;"
```

## 🔒 Security Notes

- Default passwords are for development only
- Never commit API keys to version control
- Use `.env` file for sensitive configuration
- Consider using Docker secrets for production

## 🆘 Getting Help

If you encounter issues:

1. Check service status: `./scripts/dev-status.sh`
2. View logs: `docker-compose logs -f service-name`
3. Check Docker resources: `docker system df`
4. Reset environment: `./scripts/dev-stop.sh --clean && ./scripts/dev-start.sh`

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [GraphQL Documentation](https://graphql.org/learn/)
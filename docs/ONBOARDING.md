# 🚀 Plasma Engine Developer Onboarding

Welcome to the Plasma Engine team! This guide will get you up and running in minutes.

## 🎯 Quick Start (5 minutes)

### Prerequisites Check

```bash
# Verify Docker is installed
docker --version  # Should be 20.x or later
docker-compose --version  # Should be 2.x or later

# Verify Git
git --version  # Should be 2.x or later
```

### Three-Step Setup

```bash
# 1. Clone and enter the repository
git clone https://github.com/plasma-engine/plasma-engine-org.git
cd plasma-engine-org

# 2. Run the automated setup
chmod +x scripts/dev.sh
./scripts/dev.sh setup

# 3. Verify everything is working
./scripts/dev.sh status
```

✅ **That's it!** Your development environment is ready.

## 📍 Where to Find Things

### 🌐 Web Interfaces

| Service | URL | Purpose |
|---------|-----|---------|
| **Content UI** | http://localhost:3000 | Main application interface |
| **Agent UI** | http://localhost:3001 | Agent workflow builder |
| **API Gateway** | http://localhost:8000/docs | Unified API (Swagger UI) |
| **Database UI** | http://localhost:8080 | Adminer for PostgreSQL |
| **Mail Testing** | http://localhost:8025 | MailHog for email testing |

### 🔑 Test Accounts

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@plasma.dev | password123 |
| **Regular User** | user@plasma.dev | password123 |
| **Developer** | dev@plasma.dev | password123 |

## 💻 Daily Workflow

### Morning Startup

```bash
# Start all services
./scripts/dev.sh start

# Check service health
./scripts/dev.sh status

# View service URLs
./scripts/dev.sh urls
```

### During Development

```bash
# View logs for debugging
./scripts/dev.sh logs          # All services
./scripts/dev.sh logs gateway  # Specific service

# Execute commands in containers
./scripts/dev.sh exec gateway bash     # Shell access
./scripts/dev.sh exec research pytest  # Run tests

# Hot reload is enabled - just save your files!
```

### End of Day

```bash
# Stop all services
./scripts/dev.sh stop

# Or keep infrastructure running (faster startup tomorrow)
docker-compose stop gateway research brand content agent
```

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                  │
│  ┌─────────────────┐        ┌─────────────────┐        │
│  │   Content UI    │        │    Agent UI     │        │
│  │    Port 3000    │        │    Port 3001    │        │
│  └────────┬────────┘        └────────┬────────┘        │
└───────────┼───────────────────────────┼─────────────────┘
            │                           │
┌───────────▼───────────────────────────▼─────────────────┐
│                  API Gateway (FastAPI)                  │
│                      Port 8000                          │
│                   Authentication / GraphQL              │
└───────────┬───────────────────────────┬─────────────────┘
            │                           │
┌───────────▼───────────────────────────▼─────────────────┐
│                   Microservices (Python)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Research │  │  Brand   │  │  Agent   │             │
│  │Port 8001 │  │Port 8002 │  │Port 8003 │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└──────────────────────────────────────────────────────────┘
            │                           │
┌───────────▼───────────────────────────▼─────────────────┐
│                    Infrastructure                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │PostgreSQL│  │  Redis   │  │  Neo4j   │  │RabbitMQ││
│  │Port 5432 │  │Port 6379 │  │Port 7474 │  │Port5672││
│  └──────────┘  └──────────┘  └──────────┘  └────────┘│
└──────────────────────────────────────────────────────────┘
```

## 🧰 Essential Commands

### Service Management

```bash
# Start/stop services
make up          # Start all services
make down        # Stop all services
make restart     # Restart all services

# View status
make ps          # Show running services
make logs        # View all logs
make health      # Check service health
```

### Database Operations

```bash
# Database management
make db-migrate   # Run migrations
make db-reset     # Reset databases (WARNING: data loss)
make db-seed      # Load sample data
make db-backup    # Create backup
```

### Testing & Quality

```bash
# Run tests
make test         # Test all services
make test-gateway # Test specific service

# Code quality
make lint         # Run linters
make format       # Auto-format code
make type-check   # Type checking
```

### Development Tools

```bash
# Access containers
make shell-gateway   # Python shell in gateway
make shell-postgres  # PostgreSQL CLI

# Debugging
make debug-gateway   # Start with debugger attached
make profile        # Performance profiling
```

## 📚 Key Resources

### Documentation

- 📖 [Local Setup Guide](docs/development/LOCAL_SETUP.md) - Detailed setup instructions
- 🏛️ [Architecture Docs](docs/architecture/) - System design and decisions
- 🔧 [API Documentation](http://localhost:8000/docs) - Interactive API explorer
- 🎯 [Contributing Guide](CONTRIBUTING.md) - Code standards and PR process

### Service-Specific Guides

- **Gateway**: Authentication, GraphQL federation, rate limiting
- **Research**: GraphRAG, vector search, knowledge graphs
- **Brand**: Social monitoring, sentiment analysis, reporting
- **Content**: AI generation, templates, publishing workflows
- **Agent**: MCP integration, workflow automation, browser control

### External Tools

- 🐳 [Docker Docs](https://docs.docker.com/)
- 🐍 [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- ⚛️ [Next.js Learn](https://nextjs.org/learn)
- 📊 [Neo4j Browser Guide](http://localhost:7474) (after starting services)

## 🎓 First Tasks

### Day 1: Environment Familiarization

1. ✅ Complete the quick setup above
2. 📱 Log into the Content UI with test credentials
3. 🔍 Explore the API documentation at http://localhost:8000/docs
4. 💾 Check the database structure in Adminer (http://localhost:8080)

### Day 2-3: First Contribution

1. 🐛 Pick a "good first issue" from GitHub
2. 🌿 Create a feature branch
3. ✏️ Make your changes (hot reload will apply them)
4. ✅ Run tests: `./scripts/dev.sh test`
5. 📤 Submit a pull request

### Week 1: Deep Dive

1. 📚 Read through the architecture documentation
2. 🔧 Set up your IDE with recommended extensions
3. 🎯 Complete a small feature or bug fix
4. 💬 Join the team chat and introduce yourself
5. 📝 Document something you learned

## 🆘 Getting Help

### Common Issues

**Services won't start?**
```bash
# Check Docker is running
docker ps

# Reset and try again
./scripts/dev.sh cleanup
./scripts/dev.sh setup
```

**Port conflicts?**
```bash
# Edit .env file to change ports
cp .env.example .env
vim .env  # Change conflicting ports
```

**Slow performance?**
- Increase Docker Desktop memory (Settings > Resources)
- Close unnecessary applications
- Use `make up-minimal` for core services only

### Support Channels

- 💬 **Slack**: #plasma-dev channel
- 📧 **Email**: dev-team@plasma-engine.com
- 📚 **Wiki**: Internal documentation portal
- 🎥 **Office Hours**: Tuesdays & Thursdays 2-3pm

## 🎉 Welcome Aboard!

You're now part of the Plasma Engine team! We're excited to have you and look forward to your contributions.

### Next Steps

1. 🎯 Complete the onboarding checklist
2. 👥 Schedule 1:1s with team members
3. 📚 Review recent pull requests
4. 🚀 Start building something awesome!

---

**Pro Tips:**
- 💡 Use `./scripts/dev.sh` for common tasks
- 🔄 Hot reload is enabled - no need to restart services
- 📝 Document as you learn - help the next developer
- 🤝 Don't hesitate to ask questions - we're here to help!

Happy coding! 🚀
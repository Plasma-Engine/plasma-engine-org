# 🚀 Plasma Engine

<div align="center">

![Plasma Engine](https://img.shields.io/badge/Plasma-Engine-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=for-the-badge&logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=for-the-badge&logo=next.js)

**Enterprise AI Platform for Research Automation, Brand Intelligence, and Content Orchestration**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🌟 Features

### 🔍 **Social Media Intelligence**
- **Multi-Platform Scraping**: Twitter/X, Instagram, GitHub, Google News with triple-fallback architecture
- **Real-time Monitoring**: Track brand mentions, sentiment, and competitor activities
- **Advanced Analytics**: Sentiment analysis, trend detection, and market insights
- **Enterprise Scrapers**: BrightData, Apify, and ScraperAPI integration

### 🤖 **AI-Powered Services**
- **Research Automation**: GraphRAG system with parallel search and synthesis
- **Content Generation**: Multi-model AI support (OpenAI, Anthropic, Google AI, etc.)
- **Agent Orchestration**: MCP integration with browser automation
- **Brand Voice**: Maintain consistent messaging across all channels

### 📊 **Enterprise Platform**
- **Microservices Architecture**: Scalable, maintainable, and fault-tolerant
- **GraphQL Federation**: Unified API gateway with type-safe queries
- **Real-time Processing**: Event-driven architecture with message queuing
- **Comprehensive Monitoring**: Performance metrics, logging, and alerting

## 🏢 Organization Structure

The **Plasma Engine** organization manages a suite of microservices and infrastructure repositories:

| Repo | Purpose | Primary Stack |
| --- | --- | --- |
| `plasma-engine-gateway` | Auth, org management, shared APIs, webhooks | Python (FastAPI), SQLModel |
| `plasma-engine-research` | Parallel search, synthesis, knowledge ingestion | Python (Async, Celery, Neo4j) |
| `plasma-engine-brand` | Brand monitoring, analytics, reporting | Python (ETL, analytics, templating) |
| `plasma-engine-content` | Content planning, voice compliance, publishing | TypeScript (Next.js, Node workers) |
| `plasma-engine-agent` | Low-code workflow builder, agent runtime | TypeScript (Next.js UI, Node orchestrators) |
| `plasma-engine-shared` | Shared libraries: `ai` SDK wrappers, domain schemas, infra tooling | Python + TypeScript packages |
| `plasma-engine-infra` | Terraform, Helm charts, Docker Compose | HCL, YAML |

## 🛠️ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional)
- Docker & Docker Compose (optional)

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/plasma-engine-org/plasma-engine.git
cd plasma-engine

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys (see Configuration section below)

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd plasma-engine-gateway && npm install && cd ..

# Start all services
./scripts/start-services.sh

# Or start individually:
cd plasma-engine-research && uvicorn app.main:app --reload --port 8000
cd plasma-engine-brand && uvicorn app.main:app --reload --port 8001
cd plasma-engine-content && uvicorn app.main:app --reload --port 8002
cd plasma-engine-agent && uvicorn app.main:app --reload --port 8003
cd plasma-engine-gateway && npm run dev

# Access the platform
open http://localhost:3000
```

### Configuration

Required API keys in `.env`:

```env
# Web Scraping (At least one required)
BRIGHTDATA_API_TOKEN=your_token_here  # Primary for social media
APIFY_TOKEN=your_token_here           # Secondary option
SCRAPERAPI_KEY=your_key_here          # Tertiary option

# AI Providers (At least one required)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/plasma_engine
```

## 📋 DevOps & Governance

- **Process Guide**: [docs/devops-process.md](docs/devops-process.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security**: [SECURITY.md](SECURITY.md)
- **Code of Conduct**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Frontend"
        GW[Next.js Gateway<br/>:3000]
    end

    subgraph "Microservices"
        RS[Research Service<br/>:8000]
        BS[Brand Service<br/>:8001]
        CS[Content Service<br/>:8002]
        AS[Agent Service<br/>:8003]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL)]
        RD[(Redis Cache)]
        NEO[(Neo4j Graph)]
    end

    subgraph "External Services"
        SC[Web Scrapers<br/>BrightData/Apify]
        AI[AI Providers<br/>OpenAI/Anthropic]
    end

    GW --> RS
    GW --> BS
    GW --> CS
    GW --> AS

    RS --> NEO
    BS --> SC
    CS --> AI
    AS --> AI

    RS --> PG
    BS --> PG
    CS --> PG
    AS --> PG

    RS --> RD
    BS --> RD
```

## 📊 Scraping Capabilities

### Supported Platforms

| Platform | Status | Features | Scraper |
|----------|--------|----------|----------|
| **Twitter/X** | ✅ Working | Profiles, tweets, mentions | BrightData |
| **Instagram** | ✅ Working | Profiles, posts, stories | BrightData |
| **GitHub** | ✅ Working | Profiles, repos, activity | BrightData |
| **Google News** | ✅ Working | Headlines, search, topics | BrightData |
| **LinkedIn** | ⚠️ Limited | Requires authentication | BrightData |
| **TikTok** | ⚠️ Limited | Requires authentication | BrightData |
| **YouTube** | ⚠️ Limited | Requires authentication | BrightData |

### Scraping Architecture

- **Triple-Fallback System**: BrightData → Apify → ScraperAPI
- **Intelligent Routing**: Platform-specific optimization
- **Rate Limiting**: Automatic throttling and retry logic
- **Performance Metrics**: Real-time monitoring and analytics

See [Scraping Documentation](docs/scrapers/README.md) for detailed integration guide.

## Phase 0 Status

| Item | Owner | Status | Notes |
| --- | --- | --- | --- |
| Project scaffolding directories | Platform Eng | ✅ Complete | Local workspace initialized (`plasma-engine/`). |
| Initial ADRs | Platform Eng | ✅ Complete | See `docs/adrs`. |
| GitHub repositories created | Platform Eng | ✅ Complete | All service repositories live under the `Plasma-Engine` organization. |
| Shared templates & CODEOWNERS | Platform Eng | ✅ Complete | Issue/PR templates, CODEOWNERS in `plasma-engine-shared`. |
| CI/CD bootstrap | Platform Eng | ✅ Complete | Reusable workflows in `plasma-engine-infra`, CI configured for all services. |
| Service README documentation | Platform Eng | ✅ Complete | Each service has detailed README with architecture overview. |
| CodeRabbit integration | Platform Eng | ✅ Complete | `.coderabbit.yml` deployed to all repos with template sync script. |
| Project board setup | Platform Eng | 🟡 Pending | GitHub Projects board to be created (ticket PE-07). |

## Next Steps

### ✅ Completed
- **PE-01**: GitHub repositories created under the `Plasma-Engine` organization
- **PE-02**: Shared templates deployed to all repositories
- **PE-03**: Reusable CI workflows implemented in `plasma-engine-infra`
- **PE-04**: Service repositories bootstrapped with CI and documentation
- **PE-05**: CodeRabbit configuration automated across repositories
- **PE-06**: Repository skeletons seeded with runnable scaffolds

### 🚀 Ready to Execute
1. **PE-07**: [Program Project Board & Automation](docs/tickets/phase-0.md#pe-07--program-project-board--automation)

### 📝 Phase 1 Planning
- Phase 1 ticket backlog drafted in `docs/tickets/phase-1.md` (import into GitHub Projects for Sprint 1 & 2).
- Standard issue template published at `docs/tickets/issue-template.md` (reference before opening new tickets).
- Service focus areas:
  - Gateway: Authentication, GraphQL federation
  - Research: GraphRAG system, vector search
  - Brand: Social monitoring, sentiment analysis
  - Content: AI generation, publishing workflows
  - Agent: MCP integration, browser automation

## 📦 Repository Links

### Service Repositories
- [plasma-engine-gateway](./plasma-engine-gateway) - API Gateway & GraphQL Federation
- [plasma-engine-research](./plasma-engine-research) - GraphRAG & Knowledge Management
- [plasma-engine-brand](./plasma-engine-brand) - Brand Monitoring & Analytics
- [plasma-engine-content](./plasma-engine-content) - Content Generation & Publishing
- [plasma-engine-agent](./plasma-engine-agent) - Agent Orchestration & Automation

### Infrastructure Repositories
- [plasma-engine-shared](./plasma-engine-shared) - Shared Templates & Libraries
- [plasma-engine-infra](./plasma-engine-infra) - CI/CD Workflows & IaC

### Organization Files
- [Organization Overview](.github/ORGANIZATION.md)
- [Organization Profile](.github/profile/README.md)

## 📚 Documentation

### Core Documentation
- [📘 API Reference](docs/api-reference.md) - Complete API documentation
- [🏛️ Architecture Guide](docs/architecture.md) - System design and architecture
- [🔧 Development Guide](docs/development.md) - Local development setup
- [🚀 Deployment Guide](docs/deployment.md) - Production deployment instructions

### Scraping Documentation
- [🕷️ Scrapers Overview](docs/scrapers/README.md) - Web scraping infrastructure
- [📊 Test Results](docs/scrapers/TEST_RESULTS.md) - Platform test results
- [🔌 Integration Guide](docs/scrapers/INTEGRATION.md) - Scraper integration guide

### Architecture
- [ADRs](docs/adrs/) - Architecture Decision Records
- [API Docs](docs/api/) - API Documentation
- [Development Handbook](docs/development-handbook.md) - Development best practices

### Project Management
- [Phase 0 Tickets](docs/tickets/phase-0.md)
- [Phase 1 Tickets](docs/tickets/phase-1-overview.md)
- [Issue Template](docs/tickets/issue-template.md)

### Operations
- [DevOps Playbook](docs/devops-process.md)
- [Makefile Commands](Makefile) - `make help` for all commands

## 🧪 Testing

```bash
# Run all tests
pytest

# Run service-specific tests
cd plasma-engine-brand && pytest tests/

# Run scraper tests
python scripts/test_all_scrapers.py
python scripts/quick_test_scrapers.py

# Run frontend tests
cd plasma-engine-gateway && npm test
```

## 🚀 Production Deployment

### Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Scale services
docker-compose up --scale brand=3 --scale research=2
```

### Kubernetes

```bash
# Deploy with Helm
helm install plasma-engine ./charts/plasma-engine

# Check status
kubectl get pods -n plasma-engine
```

## 📈 Performance

- **API Response**: < 200ms average latency
- **Scraping Success**: 85%+ success rate
- **Uptime Target**: 99.9% SLA
- **Concurrent Users**: 10,000+ supported

## 🔐 Security

- JWT authentication for all API endpoints
- Rate limiting and DDoS protection
- Input validation and sanitization
- SQL injection prevention
- XSS and CSRF protection
- Secrets management with HashiCorp Vault

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- **Python**: Black formatter, type hints, docstrings
- **TypeScript**: ESLint, Prettier, strict mode
- **Testing**: 80%+ code coverage required
- **Documentation**: Update docs with new features

## 🔒 Security

For security issues, please see our [Security Policy](SECURITY.md).

## 🗺️ Roadmap

### Phase 1: Foundation (Current 🚧)
- [x] Microservices architecture
- [x] Web scraping infrastructure
- [x] AI provider integration
- [ ] GraphQL federation
- [ ] Authentication system

### Phase 2: Enhancement (Q2 2025)
- [ ] Advanced analytics dashboard
- [ ] Machine learning models
- [ ] Real-time notifications
- [ ] Mobile applications

### Phase 3: Scale (Q3 2025)
- [ ] Kubernetes deployment
- [ ] Global CDN integration
- [ ] Enterprise features
- [ ] API marketplace

## 📞 Support

- **Documentation**: [docs.plasma.to](https://docs.plasma.to)
- **Issues**: [GitHub Issues](https://github.com/plasma-engine-org/plasma-engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/plasma-engine-org/plasma-engine/discussions)
- **Email**: support@plasma.to
- **Twitter**: [@plasmaengine](https://twitter.com/plasmaengine)

## 📄 License

Copyright © 2025 Plasma Engine. All rights reserved.

---

<div align="center">

**Built with ❤️ by the Plasma Engine Team**

[Website](https://plasma.to) • [Twitter](https://twitter.com/plasmaengine) • [LinkedIn](https://linkedin.com/company/plasma-engine)

</div>



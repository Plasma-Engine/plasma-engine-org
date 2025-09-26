# 🚀 Plasma Engine Organization

> **Enterprise AI Platform for Research Automation, Brand Intelligence, and Content Orchestration**

[![Organization](https://img.shields.io/badge/Organization-Plasma%20Engine-blue)](https://github.com/plasma-engine)
[![Services](https://img.shields.io/badge/Services-7-green)](#repositories)
[![Phase](https://img.shields.io/badge/Phase-1-yellow)](docs/tickets/phase-1.md)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

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

```bash
# Clone all repositories
make clone-all

# Set up development environment
make setup

# Run all services
make run-all

# Access the platform
open http://localhost:3000
```

## 📋 DevOps & Governance

- **Process Guide**: [docs/devops-process.md](docs/devops-process.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security**: [SECURITY.md](SECURITY.md)
- **Code of Conduct**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

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

### Architecture
- [ADRs](docs/adrs/) - Architecture Decision Records
- [API Docs](docs/api/) - API Documentation
- [Development Guide](docs/development-handbook.md)

### Project Management
- [Phase 0 Tickets](docs/tickets/phase-0.md)
- [Phase 1 Tickets](docs/tickets/phase-1-overview.md)
- [Issue Template](docs/tickets/issue-template.md)

### Operations
- [DevOps Playbook](docs/devops-process.md)
- [Makefile Commands](Makefile) - `make help` for all commands

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 🔒 Security

For security issues, please see our [Security Policy](SECURITY.md).

## 📄 License

Copyright © 2025 Plasma Engine. All rights reserved.



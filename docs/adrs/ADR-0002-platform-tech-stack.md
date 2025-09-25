# ADR-0002: Platform Technology Stack

## Status

Accepted — 2025-09-25

## Context

Plasma Engine must deliver AI-first workflows that span research, analytics, and content automation. The stack must support:

- High-throughput async workloads (search, ingestion).
- Rich interactive dashboards and workflow builders.
- Shared AI model governance and cost tracking.
- Deployment portability across dev/staging/production.

## Decision

Adopt the following baseline technologies:

- **Backend Services**: Python 3.11+, FastAPI, SQLModel, Celery/Prefect for orchestration, PostgreSQL, Redis, Neo4j.
- **AI Layer**: `ai` SDK with OpenAI (`gpt-5`, `gpt-5-mini`, `gpt-5-nano`), Anthropic (`claude-3-7-sonnet-20250219`), Gemini (`gemini-1.5-pro`).
- **Frontends**: Next.js 15, TypeScript, Tailwind, TanStack Query, Zustand, AI SDK React utilities.
- **Workers**: Dockerized Python (research, analytics) and Node.js (content publishing, workflow runtime).
- **Infrastructure**: Docker Compose for local, Helm on Kubernetes for staging/prod, Terraform for cloud provisioning.
- **Observability**: OpenTelemetry, Prometheus/Grafana, Loki, Sentry.

## Consequences

### Positive

- Aligns with industry-standard, well-supported tooling.
- Facilitates reuse of cloned reference projects (Dify, FastGPT, trigger.dev).
- Provides flexibility in scaling compute-intensive AI tasks.

### Negative

- Multiple runtimes increase complexity (Python + Node).
- Requires disciplined DevOps investment (Helm, Terraform, observability stack).
- AI model mix demands budgeting and monitoring from day one.

## Follow-Up Actions

1. Document environment requirements per repo (runtime versions, container base images).
2. Provide starter templates (FastAPI service skeleton, Next.js app shell, worker blueprint).
3. Define cost monitoring hooks within `plasma-engine-shared` to enforce AI usage policy.


#!/bin/bash
set -euo pipefail

# Generates Phase 1 GitHub issues from ticket specs.
# Requires: gh auth login (scope: repo), ticket markdown files in docs/tickets.

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GITHUB_ORG="${GITHUB_ORG:-Plasma-Engine}"

create_issue() {
  local repo="$1"; shift
  local id="$1"; shift
  local title="$1"; shift
  local labels="$1"; shift

  local existing
  existing=$(gh issue list -R "${GITHUB_ORG}/${repo}" --search "${id}" --json number --jq 'length')
  if [[ "${existing}" != "0" ]]; then
    echo -e "  ${YELLOW}•${NC} [${id}] already exists"
    cat > /dev/null
    return
  fi

  local body_file
  body_file=$(mktemp)
  cat > "${body_file}"

  IFS=',' read -ra raw_labels <<< "${labels}"
  local label_args=()
  for label in "${raw_labels[@]}"; do
    local trimmed="$(echo "${label}" | xargs)"
    [[ -n "${trimmed}" ]] && label_args+=(--label "${trimmed}")
  done

  if gh issue create -R "${GITHUB_ORG}/${repo}" --title "[${id}] ${title}" --body-file "${body_file}" "${label_args[@]}" >/dev/null; then
    echo -e "  ${GREEN}✓${NC} Created [${id}] ${title}"
  else
    echo -e "  ${YELLOW}⚠${NC} Failed to create [${id}] ${title}"
  fi

  rm -f "${body_file}"
}

echo -e "${BLUE}Seeding Phase 1 backlog${NC}"

# Gateway
cat <<'ISSUE' | create_issue plasma-engine-gateway PE-GW-001 "Set up FastAPI application structure" "phase:1,service:gateway,type:feature,priority:high"
## Summary
Initialize FastAPI application with modular project layout, dependency injection container, and configuration management.

## Acceptance Criteria
- FastAPI app bootstraps with settings module, logging, and DI container
- Health check endpoints exist for liveness and readiness
- Base routers registered with versioned prefix
- Error handling middleware configured for structured responses
- Unit test scaffold in place

## Tasks
- [ ] Scaffold `/app` package with `api`, `core`, `services`, `schemas`
- [ ] Add Pydantic settings loading from environment and `.env`
- [ ] Configure structured logging and request ID middleware
- [ ] Implement `/health/live` and `/health/ready`
- [ ] Add pytest configuration and sample test
ISSUE

cat <<'ISSUE' | create_issue plasma-engine-gateway PE-GW-002 "Implement JWT authentication" "phase:1,service:gateway,type:feature,priority:critical"
## Summary
Provide organization-level authentication with JWT access tokens, refresh tokens, and role-based policies.

## Acceptance Criteria
- Login endpoint validates credentials and issues access + refresh token pair
- Refresh endpoint rotates tokens securely
- Role-based guard middleware available for route protection
- Tokens signed with configured secret and include org/tenant claims
- Negative paths covered by tests (expired, invalid signature, revoked)

## Tasks
- [ ] Define auth domain models and Pydantic schemas
- [ ] Implement password hashing + verification helpers
- [ ] Create token service with rotation + blacklist support
- [ ] Add FastAPI dependencies for `CurrentUser` and `RequireRole`
- [ ] Cover critical flows with pytest unit tests
ISSUE

cat <<'ISSUE' | create_issue plasma-engine-gateway PE-GW-003 "GraphQL Federation setup" "phase:1,service:gateway,type:feature,priority:high"
## Summary
Introduce Apollo Federation gateway to compose schemas across Plasma Engine services with authentication and observability hooks.

## Acceptance Criteria
- Apollo router configured with service list and health probes
- Federation schemas validated in CI
- Auth token propagation middleware adds org/user context to downstream services
- Query complexity guard configured with sane defaults
- Gateway metrics exported via Prometheus endpoint

## Tasks
- [ ] Define federation configuration referencing service endpoints
- [ ] Add schema registry or composition script in CI
- [ ] Implement auth header forwarding and tracing middleware
- [ ] Configure rate limiting / complexity guard
- [ ] Document local dev startup instructions in README
ISSUE

# Research
cat <<'ISSUE' | create_issue plasma-engine-research PE-RS-001 "GraphRAG core implementation" "phase:1,service:research,type:feature,priority:critical,ai:graphrag"
## Summary
Build the foundational GraphRAG engine combining Neo4j graph storage with vector embeddings and retrieval workflows.

## Acceptance Criteria
- Neo4j schema defined for entities, relationships, and provenance metadata
- Embedding generation supports OpenAI + Azure providers via AI SDK
- Graph construction pipeline converts document chunks into graph nodes with relationships
- Retrieval API performs hybrid search (vector + graph traversal)
- Unit / integration tests cover ingestion and retrieval flows

## Tasks
- [ ] Set up Neo4j driver configuration and connection pooling
- [ ] Implement embedding service abstractions with retries + fallbacks
- [ ] Build chunk -> node transformation with metadata enrichment
- [ ] Implement retrieval service returning ranked context bundles
- [ ] Add pytest integration suite using dockerized Neo4j
ISSUE

cat <<'ISSUE' | create_issue plasma-engine-research PE-RS-002 "Multi-source search orchestration" "phase:1,service:research,type:feature,priority:high"
## Summary
Support federated search across web, academic, and knowledge-base sources with aggregation and scoring.

## Acceptance Criteria
- Source adapters exist for at least WebSearch, ArXiv, GitHub, and InternalDocs
- Orchestrator executes searches in parallel with circuit breaker + timeout controls
- Aggregated results include relevance scoring and source metadata
- Caching layer prevents repeated upstream calls
- Observability metrics for latency, success rate, and errors

## Tasks
- [ ] Define source adapter interface with common contract
- [ ] Implement async execution with retries and deadlines
- [ ] Build ranking aggregator merging per-source scores
- [ ] Add Redis caching with configurable TTL per source
- [ ] Instrument with OpenTelemetry metrics + tracing
ISSUE

cat <<'ISSUE' | create_issue plasma-engine-research PE-RS-003 "Knowledge ingestion pipeline" "phase:1,service:research,type:feature,priority:high,ai:graphrag"
## Summary
Create ingestion workflows to continuously add new knowledge from files, web captures, and transcripts into GraphRAG.

## Acceptance Criteria
- Ingestion jobs for PDFs, HTML, and transcripts persist normalized documents
- Chunking strategies configurable per content type
- Entities and relationships extracted using LLM or NER models
- Incremental updates merge without duplicates
- Monitoring alerts on ingestion failures

## Tasks
- [ ] Build Celery/Prefect flow definitions for each ingestion source
- [ ] Implement content normalization + cleaning utilities
- [ ] Integrate entity extraction with confidence thresholds
- [ ] Write merge logic for upserts in Neo4j
- [ ] Configure Sentry alerts and metrics dashboards
ISSUE

# Brand
cat <<'ISSUE' | create_issue plasma-engine-brand PE-BR-001 "Social media monitoring setup" "phase:1,service:brand,type:feature,priority:high"
## Summary
Implement collectors for Twitter/X, LinkedIn, Reddit, and news RSS to monitor brand mentions.

## Acceptance Criteria
- Workers ingest data from core channels with rate-limit aware scheduling
- Unified schema stores post metadata and engagement stats
- Deduplication prevents reprocessing identical content
- Daily summary report generated and stored to analytics store
- Dashboard endpoint exposes aggregated KPIs

## Tasks
- [ ] Configure API integrations + secrets management for each source
- [ ] Implement queue-backed ingestion workers with retry policies
- [ ] Normalize records into shared schema with source tagging
- [ ] Generate daily aggregation job + store results
- [ ] Build FastAPI endpoint for monitoring insights
ISSUE

cat <<'ISSUE' | create_issue plasma-engine-brand PE-BR-002 "Sentiment analysis engine" "phase:1,service:brand,type:feature,priority:medium,ai:llm"
## Summary
Provide sentiment and tone analysis for collected brand mentions with alert thresholds.

## Acceptance Criteria
- Sentiment pipeline supports multilingual content
- Outputs overall polarity, emotion scores, and confidence values
- Alerts trigger when negative sentiment crosses threshold
- Results stored with traceability to original record
- Evaluation harness benchmarks accuracy across sample set

## Tasks
- [ ] Integrate AI SDK sentiment models with fallbacks
- [ ] Implement batching + rate limiting for inference calls
- [ ] Create alerting rules and Slack/Webhook notifier
- [ ] Store sentiment results in analytics warehouse
- [ ] Build evaluation notebook + automated tests
ISSUE

# Content
cat <<'ISSUE' | create_issue plasma-engine-content PE-CT-001 "AI content generation pipeline" "phase:1,service:content,type:feature,priority:high,ai:llm"
## Summary
Build AI-assisted content generation pipeline with templates, guardrails, and human-in-the-loop review.

## Acceptance Criteria
- Templates defined for core content types (newsletter, blog, social)
- Generation workflow supports multiple LLM providers with fallback
- Compliance guardrails enforce brand voice + banned phrases
- Draft review queue with status transitions (draft, review, approved)
- Tests cover generation service and guardrail logic

## Tasks
- [ ] Define content schema + validation rules
- [ ] Integrate AI SDK generateText with streaming + retries
- [ ] Implement prompt templating + guardrail checks
- [ ] Build review workflow API + persistence models
- [ ] Add unit + snapshot tests for representative outputs
ISSUE

cat <<'ISSUE' | create_issue plasma-engine-content PE-CT-002 "Multi-platform publishing" "phase:1,service:content,type:feature,priority:medium"
## Summary
Enable publishing of approved content to web, email, and social platforms with scheduling.

## Acceptance Criteria
- Connectors exist for Web CMS, Email, and Social APIs
- Scheduling queue handles immediate + timed publish
- Publishing audit log records status + response metadata
- Retries with exponential backoff for transient failures
- Dashboard endpoint lists upcoming and recent publishes

## Tasks
- [ ] Implement provider SDK adapters with secrets management
- [ ] Build scheduler service integrated with Celery/Prefect
- [ ] Create audit logging tables and API
- [ ] Add retry + dead-letter queue handling
- [ ] Document runbook for publishing failures
ISSUE

# Agent
cat <<'ISSUE' | create_issue plasma-engine-agent PE-AG-001 "MCP server integration" "phase:1,service:agent,type:feature,priority:critical"
## Summary
Integrate Model Context Protocol server to orchestrate multi-agent workflows with tool calling support.

## Acceptance Criteria
- MCP server exposes Plasma Engine tools with schema validation
- Conversation state persisted for long-running workflows
- Tools support auth propagation and rate limiting
- Agent orchestration engine supports branching plans + retries
- Integration tests simulate end-to-end agent execution

## Tasks
- [ ] Implement MCP server scaffold with health endpoints
- [ ] Register core tools (search, content, brand monitoring)
- [ ] Add Redis/Postgres-backed conversation storage
- [ ] Build orchestration state machine with retries + compensation
- [ ] Add integration tests using mocked MCP client
ISSUE

cat <<'ISSUE' | create_issue plasma-engine-agent PE-AG-002 "Browser automation framework" "phase:1,service:agent,type:feature,priority:high"
## Summary
Provide Playwright-based automation to let agents interact with web properties safely.

## Acceptance Criteria
- Playwright worker pool with isolation per task
- Action abstraction supports navigate, fill, click, evaluate, download
- Screenshot + DOM snapshot capture for debugging
- Error recovery with automatic retries + human handoff channel
- Security guardrails prevent unintended domains and credential leaks

## Tasks
- [ ] Containerize Playwright worker image with necessary deps
- [ ] Implement task queue + lifecycle management
- [ ] Create action API with validation + timeouts
- [ ] Add telemetry + screenshot storage
- [ ] Document runbook for automation failures
ISSUE

# Infrastructure
cat <<'ISSUE' | create_issue plasma-engine-infra PE-INF-001 "Kubernetes manifests" "phase:1,service:infra,type:infrastructure,priority:high"
## Summary
Author base Kubernetes manifests (Helm charts) for all services including config, secrets, and networking.

## Acceptance Criteria
- Helm chart per service with configurable resources + env vars
- Shared chart library for ingress/autoscaling patterns
- Secrets managed via External Secrets with cloud KMS integration
- Ingress supports staging + production domains
- CI renders manifests and runs kubeval/kubeconform

## Tasks
- [ ] Scaffold Helm chart structure in `plasma-engine-infra`
- [ ] Define values schema + default values
- [ ] Integrate External Secrets + secret templates
- [ ] Configure ingress + service mesh annotations
- [ ] Add CI job to lint and template manifests
ISSUE

cat <<'ISSUE' | create_issue plasma-engine-infra PE-INF-002 "Terraform infrastructure" "phase:1,service:infra,type:infrastructure,priority:high"
## Summary
Provision core cloud infrastructure (networking, databases, storage, observability stack) using Terraform modules.

## Acceptance Criteria
- Environment-specific workspaces for dev/staging/prod
- Modules for VPC/networking, Kubernetes, Postgres, Redis, storage, monitoring
- Remote state stored securely with locking
- CI validates terraform fmt/validate and plan
- Documentation covers bootstrap and promotion workflow

## Tasks
- [ ] Create module structure + root modules per environment
- [ ] Configure backend state (e.g., S3 + DynamoDB)
- [ ] Define providers and credentials via GitHub Actions OIDC
- [ ] Implement core infrastructure resources
- [ ] Add CI pipeline for terraform fmt/validate/plan
ISSUE

cat <<'ISSUE' | create_issue plasma-engine-infra PE-INF-003 "Monitoring stack" "phase:1,service:infra,type:infrastructure,priority:medium"
## Summary
Deploy monitoring stack (Prometheus, Grafana, Loki, Tempo, Alertmanager) with dashboards and alerts.

## Acceptance Criteria
- Monitoring stack installed via Helm with persistence
- Service dashboards for latency, errors, throughput, resource usage
- Alerting rules defined for SLO breaches and infrastructure incidents
- Logs ingested into Loki with structured fields
- Incident runbook documented and linked from dashboard

## Tasks
- [ ] Deploy kube-prometheus-stack with customization
- [ ] Configure Grafana dashboards + folder structure
- [ ] Set up Loki + Promtail for log ingestion
- [ ] Define Alertmanager routes + notification channels
- [ ] Document monitoring + alert response playbook
ISSUE

print_success() {
  echo -e "\n${GREEN}Phase 1 backlog is synchronized.${NC}"
}

print_success

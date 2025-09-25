### Plasma Engine DevOps Lifecycle (Plan → Monitor)

Date: 2025-09-25

---

#### Scope and context
- Multi-repository program per ADR-0001 with primary repos: `plasma-engine-gateway`, `plasma-engine-research`, `plasma-engine-brand`, `plasma-engine-content`, `plasma-engine-agent`, `plasma-engine-shared`, `plasma-engine-infra`.
- Baseline stack per ADR-0002:
  - Backend: Python 3.11+, FastAPI, SQLModel, Celery/Prefect; DBs: PostgreSQL (+pgvector/TimescaleDB), Redis, Neo4j
  - Frontend/Workers: Next.js 15 (TypeScript), Tailwind; Node workers
  - Infra: Docker Compose (local), Helm on Kubernetes (staging/prod), Terraform (cloud)
  - Observability: OpenTelemetry, Prometheus/Grafana, Loki, Sentry
- CI/CD strategy per ADR-0003: GitHub Actions reusable workflows, artifact registry (`ghcr.io`), Trivy/pip-audit/npm audit, Terraform plan/apply via environments.

Inventory note
- A repository structure snapshot was generated at `docs/inventory/repo-structure.txt` (recursive). Service code resides in separate repos; this org repo centralizes governance docs, ADRs, and scripts.

---

### Phases tailored to Plasma Engine

#### Plan
- Objectives
  - Translate business goals into measurable SLIs/SLOs, compliance controls, budget targets, and cross-repo roadmap.
- Activities
  - Roadmapping in GitHub Projects; ADRs for architecture decisions; threat modeling (STRIDE) for gateway, data pipelines, and AI usage; data classification (PII/PHI/PCI) and retention policies.
- Tooling / automation
  - Issue templates, ADR templates, CODEOWNERS; Renovate config; policy-as-code baselines (Open Policy Agent/Conftest for IaC).
- Compliance hooks
  - Map SOC 2/ISO 27001 controls to repos; define secure SDLC checkpoints; require risk assessment for new data flows.
- Deliverables
  - Service SLOs and error budgets; data flow diagrams; compliance matrix; ADRs with alternatives and consequences.

#### Code
- Objectives
  - High-quality, secure, well-documented code with consistent interfaces across services.
- Activities
  - Enforce lint/format (ruff/black, eslint/prettier); typed APIs (Pydantic v2/Zod); secrets never in repo; pre-commit hooks; code reviews (CodeRabbit + human).
- Tooling / automation
  - Reusable GitHub Actions for lint/test; commit signing; secret scanning; dependency update bot.
- Compliance hooks
  - DCO/signoff, branch protections, review requirements; SBOM generation (Syft) per image.
- Deliverables
  - Passing static checks; SBOMs; architecture comments in code; API schemas.

#### Build
- Objectives
  - Reproducible, minimal, secure artifacts for Python, Node, and IaC.
- Activities
  - Multi-stage Docker builds; lockfiles; deterministic versioning (semver + git SHA); build provenance (SLSA attestation if feasible).
- Tooling / automation
  - GitHub Actions build matrix; Docker Buildx; Trivy image scan; Cosign signing; cache strategy for faster CI.
- Compliance hooks
  - Store SBOMs and scan results; signed artifacts; provenance attached to releases.
- Deliverables
  - Container images in `ghcr.io/plasma-engine/*`, SBOMs, signed digests.

#### Test
- Objectives
  - Confidence via fast unit tests, targeted integration/contract tests, and security checks.
- Activities
  - Unit tests (pytest, vitest); contract tests for GraphQL/REST; performance smoke (Locust/k6); schema compatibility tests; secrets/licensing scans.
- Tooling / automation
  - Coverage gates (≥80% new/changed lines); ephemeral test containers; service stubs/mocks; OWASP ZAP/Snyk (as budget allows).
- Compliance hooks
  - Test evidence retention; traceability of requirements → tests; vulnerability thresholds with enforced gating.
- Deliverables
  - Coverage reports; contract baselines; security scan reports.

#### Release
- Objectives
  - Predictable, reversible release process with approvals and audit trail.
- Activities
  - Version bump + changelog; release candidates; promotion via environments; blue/green or canary plans.
- Tooling / automation
  - GitHub Releases, environment protection rules; Release Please/semantic-release; artifact immutability.
- Compliance hooks
  - Change management approvals; segregation of duties; artifact retention and release notes with CVE status.
- Deliverables
  - Signed release artifacts; change records; rollback plan per release.

#### Deploy
- Objectives
  - Safe rollouts to Kubernetes with zero/near-zero downtime and clear rollback.
- Activities
  - Helm chart values per env; progressive delivery (canary/blue-green); database migrations with backout; config/secret management.
- Tooling / automation
  - ArgoCD/GitOps; Helm 3; HashiCorp Vault or AWS Secrets Manager; Kubernetes admission policies; Pod Security Standards.
- Compliance hooks
  - Encrypted secrets at rest and in transit; mTLS service mesh; change approvals logged; least privilege for service accounts.
- Deliverables
  - Deployed releases with health checks, HPA settings, and runbooks.

#### Operate
- Objectives
  - Reliability at agreed SLOs and efficient operations.
- Activities
  - On-call rotations; incident response; capacity planning; cost optimization (FinOps tags); disaster recovery testing.
- Tooling / automation
  - Prometheus/Grafana/Loki; OpenTelemetry tracing; Alertmanager → PagerDuty; backup/restore automation; autoscaling policies.
- Compliance hooks
  - Access logs/audit trails; DR evidence (RTO/RPO); PII retention and deletion workflows.
- Deliverables
  - Runbooks, postmortems, capacity/cost reports.

#### Monitor (and Improve)
- Objectives
  - Deep observability across logs, metrics, traces, and business KPIs; continuous improvement.
- Activities
  - Define SLIs/SLOs; alert tuning; synthetic checks; user journey dashboards; DORA metrics tracking.
- Tooling / automation
  - SLO tooling (Nobl9, Sloth, or custom); error budget policies; anomaly detection; canary analysis.
- Compliance hooks
  - Monitoring of security controls; audit log retention; evidence collection for audits.
- Deliverables
  - SLO dashboards, error budget policies, monthly reliability reviews.

---

### DORA metrics and targets (initial)
- Deployment frequency: at least weekly to staging; biweekly to prod per service.
- Lead time for changes: < 1 day to staging; < 3 days to prod for standard changes.
- Change failure rate: < 15% (initial), improving as we add e2e tests.
- MTTR: < 1 hour for P1 incidents in staging; < 4 hours in prod.

---

### Compliance baseline (program level)
- Frameworks: SOC 2 Type II, ISO 27001 (baseline); GDPR for personal data; additional HIPAA controls only if handling PHI.
- Controls embedded in lifecycle:
  - Secure SDLC (design reviews, threat modeling, code scanning, SBOMs)
  - Access control (least privilege, SSO, MFA; per-repo CODEOWNERS + branch protections)
  - Change management (approvals, release notes, rollback)
  - Logging & monitoring (tamper-evident logs, retention)
  - Data governance (classification, retention, deletion)

---

### exa/eza CLI usage (repo inventory)
- Command run (with fallback): `exa -1 --classify --long --git --recurse .` → output saved to `docs/inventory/repo-structure.txt`.
- If `exa` is unavailable, `eza` supports equivalent flags (and a `--json` output for programmatic parsing). Recommended for reproducible inventories in CI.

### Exa (exa.ai) API and CLI (for later use)
- Overview
  - Exa provides semantic web search, content extraction, and similarity search APIs with SDKs (JavaScript/Python) and a simple CLI.
- Typical capabilities
  - Search: semantic results with domain/date filters; retrieve content/full text; get highlights/snippets.
  - Similarity: find pages similar to a URL or text.
  - Crawl/fetch: fetch and clean page content; batch operations.
- Common usage patterns
  - Auth via Bearer API key; JSON requests and responses; pagination via `numResults`/cursor-like tokens.
  - Filters: include/exclude domains, time windows.
  - Outputs: URLs, titles, snippets/highlights, (optionally) cleaned content.
- Note: Validate exact endpoints/parameters in `https://exa.ai/docs` before implementation.

---

### References (authoritative)
- CNCF
  - Cloud Native maturity/operating models and security (incl. supply chain): `https://www.cncf.io/` and `https://github.com/cncf/tag-security`
- AWS
  - Well-Architected Framework: `https://aws.amazon.com/architecture/well-architected/`
- Google SRE
  - SRE Books and practices: `https://sre.google/books/`
- DORA
  - Research and four key metrics: `https://dora.dev/`

---

### Immediate next actions
1) Wire up reusable GitHub Actions (lint/test/build/scan) across all service repos per ADR-0003.
2) Stand up local dev via Docker Compose (`plasma-engine-infra`) with shared Postgres/Redis/Neo4j.
3) Define SLIs/SLOs for gateway, research pipelines, and content workers; instrument with OpenTelemetry.
4) Establish secrets management (Vault/AWS SM) and baseline K8s policies (PSPs replacement: PSS/OPA).
5) Draft runbooks and incident templates; enable pager integration for staging.


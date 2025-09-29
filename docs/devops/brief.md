### DevOps lifecycle brief (Plan → Monitor), tailored to Plasma Engine monorepo

This brief maps the full DevOps lifecycle to the stack described in the repository layout: multi-service Python apps (agent/brand/content/research), a TypeScript gateway, shared tooling, and infra as code with Terraform and Docker Compose. It aligns with CNCF cloud-native guidance, AWS DevOps Guidance, Google SRE practices, and DORA metrics.

#### Plan
- Requirements and roadmapping in issues/ADRs under `docs/adrs/` and tickets under `docs/tickets/`.
- Define service ownership, SLIs/SLOs per service; capture error budgets. Reference: `sre.google` SLOs.
- Security/compliance requirements upfront: data handling, secrets policy, SBOM/attestations, change management.

Deliverables:
- Updated ADRs; service catalogs; risk register; compliance controls mapping.

#### Develop
- Python apps follow `pyproject.toml`; Node gateway uses `tsconfig.json`. Enforce code style, typing, and tests.
- Trunk-based development with short-lived branches; mandatory code reviews.
- Secretless dev: use environment files with a secrets manager in CI.

Controls:
- Static analysis (ruff/mypy for Python; eslint/tsc for TS), SCA (pip-audit/npm audit), secret scanning, license checks.

#### Build
- Reproducible builds for Python wheels and Node artifacts; container images per service.
- SBOM generation (CycloneDX/Syft) and provenance (SLSA attestations) for each build.

Controls:
- Build in isolated runners; sign artifacts and images (cosign). Store artifacts in a registry.

#### Test
- Unit and integration tests in each service’s `tests/`.
- Contract tests for gateway ↔ services; e2e smoke in ephemeral envs.
- Security tests: dependency vulns, basic DAST for HTTP endpoints.

Quality gates:
- Coverage thresholds, lint clean, severity thresholds for SCA.

#### Release
- Versioning per service (semver). Automated changelogs and release notes.
- Promote artifacts via environments (dev → staging → prod) with approvals.

Change management:
- Link releases to tickets/ADRs; maintain audit trail for compliance.

#### Deploy
- IaC via Terraform (`plasma-engine-infra/terraform`) for cloud infra.
- Containers orchestrated (future-ready for Kubernetes); blue/green or canary for gateway.
- Database migrations as code with automated roll-forward/rollback.

Controls:
- Runtime configuration via env; secrets from manager (e.g., AWS Secrets Manager).

#### Operate
- Observability: metrics, logs, traces. Define SLIs/SLOs; alert on error budget burn rate.
- Incident response: on-call rotation, runbooks, blameless postmortems.
- Cost monitoring and capacity planning.

#### Monitor (and Learn)
- Dashboards per service and business KPIs; DORA metrics (deploy freq, lead time, change fail rate, MTTR).
- Feedback loops into backlog; periodic reliability reviews.

Compliance considerations (cross-cutting)
- Supply chain: SBOM, signature verification (cosign, policy-controller), provenance (SLSA).
- Access: least privilege, IAM roles for CI/CD, scoped tokens.
- Data: encryption in transit/at rest, data retention policies, DPIA as needed.
- Audit: immutable logs, evidence retention, periodic control testing.

References (authoritative)
- AWS DevOps Guidance (Well-Architected): `https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/devops-guidance.html`
- Google SRE SLOs: `https://sre.google/sre-book/service-level-objectives/`
- DORA overview and metrics: `https://dora.dev/` and `https://cloud.google.com/devops/`
- CNCF Security WG Whitepaper (supply chain/SBOM): `https://github.com/cncf/tag-security/tree/main/security-whitepaper`
- SLSA framework: `https://slsa.dev/`


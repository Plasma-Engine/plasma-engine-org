## Plasma Engine Orchestrator — Plan of Record (POR)

Last updated: 2025-09-26

### Goals
- Establish multi-agent orchestration loop for planning, building, testing, and PR-driven delivery across all Plasma Engine services.
- Keep changes incremental with small PRs, full lint/test coverage, and CodeRabbit reviews.
- Maintain shared state: `ORCHESTRATOR_PLAN.md`, `WORK_LOG.md`, `TODO.yaml`, `PROGRESS.md`.

### Architecture (from ADR-0002)
- Backend services: Python 3.11+, FastAPI, SQLModel, Celery/Prefect, PostgreSQL, Redis, Neo4j.
- AI layer: ai SDK with OpenAI (gpt-5, gpt-5-mini, gpt-5-nano), Anthropic (claude-3-7-sonnet-20250219), Gemini (gemini-1.5-pro). Optimize for best-fit models per task and verify model names in vendor docs.
- Frontend: Next.js 15, TypeScript, Tailwind, TanStack Query, Zustand.
- Infrastructure: Docker Compose locally; Helm on Kubernetes; Terraform for cloud.
- Observability: OpenTelemetry, Prometheus/Grafana, Loki, Sentry.

### Service Topology and Ports (per project brief)
- Gateway (TypeScript/Apollo Federation) — port 3000
- Research (Python/FastAPI — GraphRAG, Neo4j) — port 8000
- Brand (Python/FastAPI) — port 8001
- Content (Python/FastAPI) — port 8002
- Agent (Python/FastAPI — MCP, browser automation) — port 8003
- Shared (templates, libs, docs)
- Infra (CI/CD, Terraform, Docker Compose)

### Repository Model (from ADR-0001)
Adopted multi-repo under `plasma-engine` GitHub org. Expected repos:
- plasma-engine-gateway
- plasma-engine-research
- plasma-engine-brand
- plasma-engine-content
- plasma-engine-agent
- plasma-engine-shared
- plasma-engine-infra

Local status (workspace discovery):
- Current workspace lacks service directories. Use `make clone-all` to fetch all repos into sibling folders under the root.

### Make Targets (extracted from root Makefile)
- setup: clone-all → start infra via docker-compose → install-deps → init-db
- clone-all, pull-all, status-all
- install-deps, init-db
- start-infra, stop-infra, logs, ps
- run-gateway, run-research, run-brand, run-content, run-agent, run-all (tmux-based)
- test-all, lint-all
- build-all, push-all
- docs, serve-docs
- version, tag-release
- clean, update-deps, sync-templates

### Initial Risks & Constraints
- Services not cloned locally; initial `lint-all` / `test-all` will no-op until repos exist.
- Network/credential requirements for cloning and GitHub PR creation may block automation.
- Docker/Compose must be available for infra targets.

### Near-Term Milestones
1) Bootstrap local workspace by cloning all service repos and recording mapping.
2) Establish green `lint-all` / `test-all` baseline across repos (small fixes, CI parity).
3) Identify top 3 high-leverage DX or quality improvements and ship them as small PRs.

### Top 3 High-Leverage Improvements (initial)
- CI bootstrap across repos: add `.github/workflows/ci.yml` using reusable workflow with lint/test/security stubs.
- Minimal health endpoint and pytest smoke tests in one Python service (seed pattern to replicate).
- Editor and linting standards: `.editorconfig` and `pre-commit` for Python repos; ESLint/Prettier baseline for gateway when code exists.

### First Small PR Candidate
- Repo: `plasma-engine-agent`
- Branch: `feat/agent/health-endpoint/2025-09-26`
- Scope: Add minimal FastAPI app with `/health`, pytest smoke test, `requirements.txt`, `pytest.ini`, and README update.
- Tests: `tests/test_health.py` via `pytest`
- Risks: low (isolated), ensures Makefile `test-all` runs something meaningful.

### Multi-Repo Mapping Table (to be populated after clone)
Columns: repo_path, repo_name, services, language, tests, CI status, branch, PR URL
- /workspace/plasma-engine-gateway — gateway — TypeScript (skeleton) — tests: none — CI: none — branch: main
- /workspace/plasma-engine-research — research — Python (skeleton) — tests: none — CI: none — branch: main
- /workspace/plasma-engine-brand — brand — Python (skeleton) — tests: none — CI: none — branch: main
- /workspace/plasma-engine-content — content — Python (skeleton) — tests: none — CI: none — branch: main
- /workspace/plasma-engine-agent — agent — Python (FastAPI scaffold added) — tests: 1 — CI: none — branch: feat/agent/health-endpoint/2025-09-26 (local)
- /workspace/plasma-engine-shared — shared — mixed docs/scripts — tests: n/a — CI: none — branch: main
- /workspace/plasma-engine-infra — infra — docs (skeleton) — tests: n/a — CI: none — branch: main

### Operating Loop
1) Plan tasks into `TODO.yaml` with owner-role and risk.
2) Branch per `feat/<service>/<scope>/<date>`.
3) Implement with tests and docs; follow Conventional Commits.
4) Validate: `make lint-all`, `make test-all`, targeted service runs.
5) PR with CodeRabbit review; iterate to green.
6) Auto-merge when safe; update `WORK_LOG.md` and `PROGRESS.md`.


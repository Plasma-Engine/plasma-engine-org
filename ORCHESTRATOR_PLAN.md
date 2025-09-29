# ORCHESTRATOR PLAN (POR)

Owner/Org: Plasma-Engine
Repo (root on disk): /Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org
Default branch: main
Generated: 2025-09-29

Purpose
- Coordinate multi-repo development via small, PR-driven iterations.
- Build, test, document, open PRs, trigger CodeRabbit, apply review feedback, merge when green.

Discovered repositories in this workspace
- plasma-engine-org
  - path: /Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org
  - language: unknown
  - remote: git@github.com:Plasma-Engine/plasma-engine-org.git
- plasma-engine-agent
  - path: /Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org/plasma-engine-agent
  - language: python
  - remote: git@github.com:Plasma-Engine/plasma-engine-agent.git
- plasma-engine-brand
  - path: /Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org/plasma-engine-brand
  - language: python
  - remote: git@github.com:Plasma-Engine/plasma-engine-brand.git
- plasma-engine-content
  - path: /Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org/plasma-engine-content
  - language: python
  - remote: git@github.com:Plasma-Engine/plasma-engine-content.git
- plasma-engine-core
  - path: /Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org/plasma-engine-core
  - language: python
  - remote: git@github.com:Plasma-Engine/plasma-engine-org.git
- plasma-engine-gateway
  - path: /Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org/plasma-engine-gateway
  - language: ts
  - remote: git@github.com:Plasma-Engine/plasma-engine-gateway.git
- plasma-engine-infra
  - path: /Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org/plasma-engine-infra
  - language: unknown
  - remote: git@github.com:Plasma-Engine/plasma-engine-infra.git
- plasma-engine-research
  - path: /Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org/plasma-engine-research
  - language: python
  - remote: git@github.com:Plasma-Engine/plasma-engine-research.git
- plasma-engine-shared
  - path: /Users/a004/Library/Mobile Documents/com~apple~CloudDocs/Documents/CODE_PROJECTS/plasma-engine-org/plasma-engine-shared
  - language: unknown
  - remote: git@github.com:Plasma-Engine/plasma-engine-shared.git

Standards and guardrails
- Never push directly to main; always use feature branches.
- Run lint and tests locally before opening or updating PRs.
- Keep PRs small, well-scoped, and include tests + docs updates.
- Use Conventional Commits for messages.

Initial workflow loop
1) Plan: maintain TODO.yaml with small tasks, dependencies, risk
2) Branch: feat/<service>/<scope>/<date>
3) Implement: code + tests
4) Validate: make lint-all, make test-all (where available)
5) Commit and open PR via gh CLI; request CodeRabbit review
6) Apply feedback; merge when green

Next actions
- Seed TODO.yaml with top items across services.
- Run install/lint/test where Makefiles or scripts exist.
- Open an initial PR adding this orchestration scaffold and request CodeRabbit review.

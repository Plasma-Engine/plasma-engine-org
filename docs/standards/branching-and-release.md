# Branching and Release Strategy

This strategy formalizes branch usage, versioning, and release gates across all repositories. It aligns with `docs/devops-process.md` and `CONTRIBUTING.md`.

## Branch Model
- main: Production-ready code; protected (signed commits, passing checks, linear history)
- develop: Integration branch for features; merges only via PR with passing checks
- feature/<ticket-id>-<slug>: Short-lived feature work; branch off `develop`, PR back to `develop`
- bugfix/<ticket-id>-<slug>: Same lifecycle as feature branches
- hotfix/<ticket-id>-<slug>: Emergency fixes; branch off latest release tag; PR into `main` and cherry-pick to `develop`
- release/<version>: Stabilization prior to release; fixes only; merges to `main` (tag) and `develop`

## Versioning
- Semantic Versioning (SemVer) per repository: MAJOR.MINOR.PATCH
- Conventional Commits drive changelog categories (feat, fix, perf, refactor, etc.)
- Pre-releases use `-rc.N` suffix from `release/*` branches

## Release Flow
1. Cut `release/x.y.z` from `develop`
2. CI enforces: lint, unit/integration tests, security scans; optional E2E
3. On approval, merge `release/x.y.z` into `main` and create tag `vX.Y.Z`
4. Auto-generate release notes from conventional commits
5. Merge back to `develop` to sync version bump and fixes

## Quality Gates (Protected Branches)
- Required checks before merge:
  - Linters and format checks pass (Python: Ruff/Black; TS: ESLint/Prettier)
  - Tests pass (unit required; integration when impacted or on `develop`/`main`)
  - Coverage ≥ 80% on changed areas
  - Security scans green (SAST, dependency, container)
  - Code review: CodeRabbit summary + at least one human approver

## Tagging & Artifacts
- Tags: `vX.Y.Z` on `main`
- Docker images: `ghcr.io/plasma-engine/<repo>:vX.Y.Z` and `:latest`
- SBOM: Attach Syft-generated SBOM to GitHub Release
- Provenance: SLSA provenance attestation attached when feasible

## Backports & Hotfixes
- For critical vulnerabilities or outages:
  - Branch `hotfix/<id>` from the latest `vX.Y.Z` tag
  - Cut `vX.Y.(Z+1)` upon merge to `main`
  - Cherry-pick the same commits to `develop`

## Release Candidates (RC)
- From `release/*`, publish artifacts as `-rc.N` tags
- Run extended test suites (soak, E2E) and performance checks

## Branch Protection Rules (Recommended)
- Require pull request reviews before merging (min 1 approver)
- Require status checks to pass before merging
- Require signed commits
- Require linear history (no merge commits)
- Restrict who can push to `main`

## Deprecation Policy
- Mark deprecated APIs with clear timeline; remove after two minor releases unless security concerns require faster removal
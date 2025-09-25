# ADR-0001: Multi-Repository Structure

## Status

Accepted — 2025-09-25

## Context

The Plasma Engine program spans diverse domains (research automation, brand monitoring, content creation, agent orchestration, shared infrastructure). A monorepo would complicate access control, CI runtimes, and independent release cadences. Teams require the ability to work, scale, and deploy services autonomously while sharing core libraries.

## Decision

Adopt a multi-repository model under a dedicated private GitHub organization (`plasma-engine`). Each domain receives a focused repository, while cross-cutting packages and infrastructure reside in dedicated shared repos. Standard tooling (CODEOWNERS, issue templates, security policy) will be enforced uniformly across all repos.

Primary repositories:

- `plasma-engine-gateway`
- `plasma-engine-research`
- `plasma-engine-brand`
- `plasma-engine-content`
- `plasma-engine-agent`
- `plasma-engine-shared`
- `plasma-engine-infra`

## Consequences

### Positive

- Clear ownership boundaries and access control per domain.
- Faster CI runs and targeted deployment pipelines.
- Ability to archive / version individual services without impacting others.

### Negative

- Requires tooling to keep shared dependencies in sync (package publishing, tagging).
- Increased organizational overhead (multiple repos to maintain).
- Cross-repo changes need coordination via release trains or automation.

## Follow-Up Actions

1. Bootstrap GitHub organization and private repositories.
2. Create shared GitHub Actions workflows for lint/test/build.
3. Implement automated dependency versioning (e.g., Renovate, Release Please) for `plasma-engine-shared` packages.


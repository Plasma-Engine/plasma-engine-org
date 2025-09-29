# Repository Guidelines

## Project Structure & Module Organization
The `plasma-engine-org` workspace houses one directory per service (`plasma-engine-gateway`, `plasma-engine-research`, `plasma-engine-brand`, `plasma-engine-content`, `plasma-engine-agent`) alongside shared assets (`plasma-engine-shared`, `plasma-engine-infra`). Docs and governance material live under `docs/`, while automation scripts reside in `scripts/`. Use the Makefile at the repo root as the hub for cross-repo tasks.

## Build, Test, and Development Commands
Run `make clone-all` to fetch every service and `make setup` to bootstrap common dependencies. `make run-all` starts the full stack; to focus on a single service use `make run-gateway` (replace with the target service). Quality gates run via `make lint-all` and `make test-all`. Documentation is generated with `make docs` and served locally through `make serve-docs`.

## Coding Style & Naming Conventions
TypeScript projects standardize on 2-space indentation, ESLint (strict) rules, and Prettier formatting; prefer PascalCase for React components and camelCase for functions and variables. Python services follow PEP 8 with 4-space indentation, Black for formatting, and Ruff plus MyPy for linting and typing. Shared libraries should live in `plasma-engine-shared` and expose namespaced modules to avoid collisions.

## Testing Guidelines
Python services use `pytest`; keep tests under `tests/` with files named `test_*.py`. TypeScript services rely on Vitest or Jest with specs in `__tests__/` or files ending in `.spec.ts`. Aim for comprehensive happy-path and failure coverage, and run targeted suites before invoking `make test-all` ahead of a PR. Update fixtures when schema contracts change.

## Commit & Pull Request Guidelines
Adopt Conventional Commits (`feat:`, `fix:`, `chore:`) and branch naming `feature/PE-123-summary` or `bugfix/PE-456-issue`. Pull requests should describe scope, reference related tickets, and summarize testing results; include screenshots for UI updates. Ensure linting and tests pass, respond to CodeRabbit feedback, and request human review before merging into `develop`.

## Security & Configuration Tips
Copy `.env.example` to `.env` per service without committing secrets. Use the shared Compose stack from `plasma-engine-infra` for local dependencies, and rotate API keys stored in your password manager. Report vulnerabilities through the security disclosure process outlined in `SECURITY.md`.

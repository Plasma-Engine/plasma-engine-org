# Testing Strategy and Quality Gates

This strategy defines the test types, coverage expectations, branch gates, and execution model across all services. It complements `CONTRIBUTING.md` and `docs/devops-process.md`.

## Test Types
- Unit Tests: Small, isolated, no external I/O by default
- Integration Tests: Exercise modules with real dependencies (DB, cache) via Testcontainers or docker-compose
- End-to-End (E2E) Tests: Full workflow via API/UI against ephemeral stacks
- Contract/Schema Tests: Ensure API/GraphQL/OpenAPI contracts remain backward compatible

## Directory & Naming Conventions
- Python: `tests/unit/`, `tests/integration/`, `tests/e2e/`; test files named `test_*.py`
- TypeScript: `tests/unit/`, `tests/integration/`, `tests/e2e/`; test files named `*.test.ts`
- Keep tests co-located with domain modules when it improves readability (acceptable) but prefer centralized `tests/` for larger services

## Coverage Targets
- Global Coverage: ≥ 80% line coverage required on PRs (changed code focus)
- Critical Modules: Security/auth, data access layers aim for ≥ 90%
- E2E Coverage: Not counted toward line coverage; tracked via scenario completion metrics

## Quality Gates (CI)
- Lint & Format: must pass
- Unit Tests: must pass on PRs to `develop` and `main`
- Integration Tests: run on PRs labeled `integration-required` or when touching affected modules; always run on `develop` and `main`
- E2E Tests: run nightly and on release candidates; optional on regular PRs unless labeled `e2e-required`
- Coverage: fail PR if coverage < threshold

## Test Matrix (by stack)
- Python Services (FastAPI, workers):
  - Unit: pytest + coverage
  - Integration: pytest + Testcontainers (Postgres, Redis, Neo4j as needed)
  - E2E: Playwright or HTTP workflow tests against ephemeral env
- TypeScript Services (Node workers, Next.js):
  - Unit: Vitest/Jest + ts-node/ts-jest
  - Integration: Testcontainers + docker-compose
  - E2E: Playwright

## Local Commands (reference)
```bash
# Python
pytest -q
pytest --cov=app --cov-report=term-missing

# TypeScript
npm test
npm run test:coverage

# E2E (Playwright)
npx playwright test --reporter=list
```

## Flakiness & Parallelism
- Mark flaky tests with `@pytest.mark.flaky` or `test.fixme` and fix within 1 sprint
- Prefer idempotent setup/teardown; randomize ports; unique schema names per run
- Run tests in parallel where possible (`pytest -n auto`, `vitest --run --maxWorkers`)

## Data Management
- Use factories/builders for test data; avoid hard-coded IDs
- Prefer ephemeral containers over shared state; reset DBs between tests

## Contract Testing
- Generate OpenAPI/GraphQL schemas on CI and diff against baseline
- Fail PRs on breaking changes unless `breaking-change` label and release notes prepared

## Example CI Stage Ordering (reusable workflow)
```yaml
jobs:
  lint_test:
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - name: Install dependencies (Python)
        run: pip install -r requirements-dev.txt || true
      - name: Install dependencies (Node)
        run: npm ci || true
      - name: Lint & Format
        run: |
          ruff check . || exit 1
          black --check . || exit 1
          npm run lint || exit 1
          npm run format:check || true
      - name: Unit Tests (Python)
        run: pytest --cov=app --cov-report=xml
      - name: Unit Tests (Node)
        run: npm run test:coverage --if-present
      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

## Exit Criteria per Test Type
- Unit: Green build + minimum coverage
- Integration: All critical paths (DB, cache, external APIs) exercised; no nondeterminism
- E2E: Happy paths and critical error paths pass; no sensitive data leaks

## Ownership & Enforcement
- Codeowners must approve changes reducing coverage in owned areas
- CI required checks enforce gates on protected branches
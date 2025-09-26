### Test Playbook

This playbook defines a layered test strategy and quality gates to support rapid, safe delivery.

#### Objectives
- Shift-left automated testing; keep master green.
- Enforce coverage and critical-path tests.

#### Practices
- Unit → Integration → E2E → Perf → Security tests in CI.
  - Source: DORA practices for CI/CD and testing: https://cloud.google.com/architecture/devops
- Observability-driven testing (contract tests with SLO-aware thresholds).
  - Source: CNCF Observability whitepaper: https://tag-observability.cncf.io/whitepaper/

#### Checklist
- Fast unit tests covering core logic
- Integration tests with representative data
- E2E smoke on each merge; perf tests before release
- Security tests (DAST/SAST) pass

#### Metrics
- Test duration by layer; flake rate
- Code coverage for new/changed lines

#### TODOs (org-specific)
- TODO: Define coverage thresholds by repo
- TODO: Link to test data management policy
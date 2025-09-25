### Runbook: CI/CD Pipeline Triage & Fix

Symptoms
- Failing or flaky jobs, long queue times, or missing required checks.

Steps
1) Identify failing stage (Lint/Test/Security/Build/Deploy) and failing repo.
2) Open linked logs and artifacts; capture error signatures.
3) Check recent changes to reusable workflows and action versions.
4) Re-run jobs with debug logging if needed.
5) For flaky tests: isolate, quarantine behind a flag, and open an issue to deflake.
6) For infra failures: validate credentials/secrets, runner capacity, and rate limits.
7) Implement fix via PR to the reusable workflow or the service repo.

Commands (local fast feedback)
```bash
make lint-all
make test-all
```

References
- ADR-0003 reusable workflows
- Exa: exa://plasma-engine/ci-troubleshooting


### Engineering PR Checklist

Use this before opening or merging a pull request.

- [ ] Issue linked in title and description (e.g., `[PE-123]`)
- [ ] ADR impact considered and linked (if applicable)
- [ ] Tests added/updated; coverage ≥80% for new/changed modules
- [ ] Lint passes locally (`make lint-all` where applicable)
- [ ] Security scan clean (pip-audit / npm audit / Trivy in CI)
- [ ] Docs updated (README, API docs, or comments where appropriate)
- [ ] Observability added/updated (logs, metrics, traces)
- [ ] Breaking changes documented with migration/compat plan
- [ ] CI status checks passing (Lint, Test, Security, Build)
- [ ] CodeRabbit review complete + one human approval

References
- DevOps Guide: `docs/devops-process.md`
- ADRs: `docs/adrs/*`
- Exa: exa://plasma-engine/ci-cd-standards


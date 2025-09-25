<!--
Explainer: CI directory hosts shared notes and reusable components for
pipeline stages. Workflows live in `.github/workflows/`.
-->

# CI Notes

- Lint: terraform fmt, markdownlint (TBD)
- Test: pytest/js tests when services land in monorepo
- Build: container images or docs artifacts
- Security: IaC scans, dependency audits
- Deploy: gated via environments
- Rollback: manual gate until release infra exists


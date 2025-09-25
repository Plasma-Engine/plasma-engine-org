### Runbook: Bootstrap a New Service

Intent: Create a new repo/service aligned with org conventions and CI.

Pre-reqs
- GitHub access and permissions to create repos
- Local Docker and Python/Node toolchains

Steps
1) Create repo using templates (see `plasma-engine-shared` templates via `scripts/sync-templates.sh`).
2) Initialize CI by adding reusable workflows per ADR-0003.
3) Add CODEOWNERS, issue and PR templates, branch protection.
4) Add health endpoint and minimal tests.
5) Document local run and CI instructions in README.

Commands (examples)
```bash
# From org root (when sub-repos are available)
./scripts/create-personal-repos.sh | cat

# Install deps within the new repo
pip install -r requirements.txt || true
npm install || true

# Run tests
pytest -q || true
npm test --silent | cat || true
```

Post-steps
- Open PR with `[PE-###]` and follow `engineering-pr-checklist.md`.
- Ensure dashboards and logging are in place before first release.

References
- DevOps Guide: `docs/devops-process.md`
- ADR-0001 multi-repo structure
- ADR-0003 CI/CD bootstrap
- Exa: exa://plasma-engine/service-bootstrap-guide

